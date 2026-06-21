import math
import random
import sys

import pygame

WIDTH, HEIGHT = 1280, 720
FPS = 60

CELL = 64
FOV = math.radians(75)
HALF_FOV = FOV * 0.5
PROJ_PLANE = (WIDTH * 0.5) / math.tan(HALF_FOV)
MAX_DEPTH = CELL * 24

MOUSE_SENS = 0.0025
MOVE_SPEED = 250
WALK_MULT = 0.58

PLAYER_R = 16
ENEMY_R = 14
ENEMY_SPEED = 120
ENEMY_SEPARATION = 26

BULLET_DAMAGE = 34
FIRE_COOLDOWN = 0.12
SHOT_RANGE = MAX_DEPTH

MAG_SIZE = 20
RESERVE = 100
RELOAD_TIME = 1.5

RECOIL_KICK = 0.018
RECOIL_JITTER = 0.006
RECOIL_RECOVERY = 7.5
SPREAD_BASE = 0.01
SPREAD_RECOIL_SCALE = 0.025

ROUND_TIME = 95.0
BUY_TIME = 8.0
SITE_R = 70
PLANT_TIME = 2.8
DEFUSE_TIME = 4.5
BOMB_TIME = 30.0

MAP_GRID = [
    "########################",
    "#....#.......#.........#",
    "#....#.......#..###....#",
    "#....#.......#.........#",
    "#....#.###...#....##...#",
    "#......###........##...#",
    "#..##......####........#",
    "#..##..........#.......#",
    "#......####....#..##...#",
    "#..............#..##...#",
    "#..######..##..#.......#",
    "#...........#..#####...#",
    "#..####.....#......#...#",
    "#.......##..#..##..#...#",
    "#......................#",
    "########################",
]

MAP_W = len(MAP_GRID[0])
MAP_H = len(MAP_GRID)
WORLD_W = MAP_W * CELL
WORLD_H = MAP_H * CELL


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def wrap_angle(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def angle_to_vec(a):
    return pygame.Vector2(math.cos(a), math.sin(a))


class Actor:
    def __init__(self, x, y, team, hp, radius):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.team = team
        self.hp = hp
        self.radius = radius
        self.dead = False
        self.angle = 0.0
        self.fire_cd = 0.0
        self.mag = MAG_SIZE
        self.reserve = RESERVE
        self.reloading = 0.0

        self.strafe_pref = random.choice([-1, 1])
        self.repath_t = random.uniform(0.25, 0.7)
        self.last_seen = None

    def can_shoot(self):
        return (not self.dead) and self.reloading <= 0 and self.fire_cd <= 0 and self.mag > 0

    def hit(self, dmg):
        if self.dead:
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.dead = True


class Tracer:
    def __init__(self, start, end, team):
        self.start = pygame.Vector2(start)
        self.end = pygame.Vector2(end)
        self.team = team
        self.life = 0.08

    def update(self, dt):
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CS2 Prototype - 2.5D FPS")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 20)
        self.big = pygame.font.SysFont("consolas", 42, bold=True)
        self.small = pygame.font.SysFont("consolas", 15)

        self.mouse_captured = True
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        self.site = pygame.Vector2(20.5 * CELL, 7.5 * CELL)
        self.enemy_spawns = [
            pygame.Vector2(17.5 * CELL, 2.5 * CELL),
            pygame.Vector2(20.5 * CELL, 3.5 * CELL),
            pygame.Vector2(18.5 * CELL, 9.5 * CELL),
            pygame.Vector2(21.0 * CELL, 12.0 * CELL),
            pygame.Vector2(16.5 * CELL, 13.0 * CELL),
            pygame.Vector2(19.0 * CELL, 6.0 * CELL),
        ]

        self.score_ct = 0
        self.score_t = 0
        self.feed = []

        self.depth_buffer = [MAX_DEPTH] * WIDTH
        self.tracers = []

        self.recoil = 0.0

        self.reset_round()

    def reset_round(self):
        self.player = Actor(2.5 * CELL, 8.5 * CELL, "T", 100, PLAYER_R)
        self.player.angle = 0.0

        self.enemies = []
        for sp in random.sample(self.enemy_spawns, 5):
            self.enemies.append(Actor(sp.x, sp.y, "CT", 68, ENEMY_R))

        self.state = "buy"
        self.buy = BUY_TIME
        self.round_time = ROUND_TIME
        self.bomb_planted = False
        self.bomb = BOMB_TIME
        self.progress = 0.0
        self.end_text = ""
        self.end_timer = 0.0

    def map_tile(self, tx, ty):
        if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
            return "#"
        return MAP_GRID[ty][tx]

    def is_solid_world(self, x, y):
        tx = int(x // CELL)
        ty = int(y // CELL)
        return self.map_tile(tx, ty) == "#"

    def circle_wall(self, p, r):
        min_tx = int((p.x - r) // CELL)
        max_tx = int((p.x + r) // CELL)
        min_ty = int((p.y - r) // CELL)
        max_ty = int((p.y + r) // CELL)

        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if self.map_tile(tx, ty) != "#":
                    continue
                left = tx * CELL
                top = ty * CELL
                nx = clamp(p.x, left, left + CELL)
                ny = clamp(p.y, top, top + CELL)
                dx = p.x - nx
                dy = p.y - ny
                if dx * dx + dy * dy <= r * r:
                    return True
        return False

    def move(self, a, dt):
        a.pos.x += a.vel.x * dt
        a.pos.x = clamp(a.pos.x, 1 + a.radius, WORLD_W - 1 - a.radius)
        if self.circle_wall(a.pos, a.radius):
            a.pos.x -= a.vel.x * dt

        a.pos.y += a.vel.y * dt
        a.pos.y = clamp(a.pos.y, 1 + a.radius, WORLD_H - 1 - a.radius)
        if self.circle_wall(a.pos, a.radius):
            a.pos.y -= a.vel.y * dt

    def cast_ray(self, origin, angle, max_dist=MAX_DEPTH):
        ox, oy = origin.x, origin.y
        dir_x = math.cos(angle)
        dir_y = math.sin(angle)

        map_x = int(ox // CELL)
        map_y = int(oy // CELL)

        if abs(dir_x) < 1e-8:
            delta_x = 1e9
            side_x = 1e9
            step_x = 0
        elif dir_x > 0:
            step_x = 1
            delta_x = CELL / dir_x
            side_x = ((map_x + 1) * CELL - ox) / dir_x
        else:
            step_x = -1
            delta_x = -CELL / dir_x
            side_x = (ox - map_x * CELL) / -dir_x

        if abs(dir_y) < 1e-8:
            delta_y = 1e9
            side_y = 1e9
            step_y = 0
        elif dir_y > 0:
            step_y = 1
            delta_y = CELL / dir_y
            side_y = ((map_y + 1) * CELL - oy) / dir_y
        else:
            step_y = -1
            delta_y = -CELL / dir_y
            side_y = (oy - map_y * CELL) / -dir_y

        dist = 0.0
        side = 0
        while dist < max_dist:
            if side_x < side_y:
                map_x += step_x
                dist = side_x
                side_x += delta_x
                side = 0
            else:
                map_y += step_y
                dist = side_y
                side_y += delta_y
                side = 1

            if self.map_tile(map_x, map_y) == "#":
                hit_x = ox + dir_x * dist
                hit_y = oy + dir_y * dist
                return dist, side, hit_x, hit_y

        hit_x = ox + dir_x * max_dist
        hit_y = oy + dir_y * max_dist
        return max_dist, side, hit_x, hit_y

    def has_los(self, start, end):
        to_t = end - start
        dist = to_t.length()
        if dist <= 1e-5:
            return True
        ang = math.atan2(to_t.y, to_t.x)
        hit_dist, _, _, _ = self.cast_ray(start, ang, dist + 2)
        return hit_dist >= dist - 1.0

    def ray_target_hit(self, origin, direction, max_dist, targets):
        nearest = None
        nearest_dist = max_dist

        for t in targets:
            if t.dead:
                continue
            rel = t.pos - origin
            proj = rel.dot(direction)
            if proj < 0 or proj > nearest_dist:
                continue

            perp2 = rel.length_squared() - proj * proj
            r = t.radius + 2
            if perp2 > r * r:
                continue

            entry = proj - math.sqrt(max(0.0, r * r - perp2))
            hit_dist = max(0.0, entry)
            if hit_dist < nearest_dist:
                nearest_dist = hit_dist
                nearest = t

        return nearest, nearest_dist

    def fire_hitscan(self, shooter, spread):
        if not shooter.can_shoot():
            return

        shooter.mag -= 1
        shooter.fire_cd = FIRE_COOLDOWN

        ang = shooter.angle + random.uniform(-spread, spread)
        d = angle_to_vec(ang)
        start = shooter.pos + d * (shooter.radius + 6)

        wall_dist, _, _, _ = self.cast_ray(start, ang, SHOT_RANGE)
        hit_point = start + d * wall_dist

        if shooter.team == "T":
            target, hit_dist = self.ray_target_hit(start, d, wall_dist, self.enemies)
            if target is not None:
                hit_point = start + d * hit_dist
                target.hit(BULLET_DAMAGE)
                if target.dead:
                    self.feed.append("You eliminated a CT")
        else:
            if not self.player.dead:
                rel = self.player.pos - start
                proj = rel.dot(d)
                if 0 <= proj <= wall_dist:
                    perp2 = rel.length_squared() - proj * proj
                    r = self.player.radius + 2
                    if perp2 <= r * r:
                        self.player.hit(BULLET_DAMAGE)
                        hit_point = start + d * max(0.0, proj)
                        if self.player.dead:
                            self.feed.append("You were eliminated")

        self.tracers.append(Tracer(start, hit_point, shooter.team))

    def update_player(self, dt):
        k = pygame.key.get_pressed()

        fwd = angle_to_vec(self.player.angle)
        right = pygame.Vector2(-fwd.y, fwd.x)

        move = pygame.Vector2(0, 0)
        if k[pygame.K_w]:
            move += fwd
        if k[pygame.K_s]:
            move -= fwd
        if k[pygame.K_a]:
            move -= right
        if k[pygame.K_d]:
            move += right

        speed = MOVE_SPEED * (WALK_MULT if k[pygame.K_LSHIFT] or k[pygame.K_RSHIFT] else 1.0)
        if move.length_squared() > 0:
            move = move.normalize() * speed
        self.player.vel = move

        mx, _ = pygame.mouse.get_rel()
        self.player.angle = wrap_angle(self.player.angle + mx * MOUSE_SENS)

        if pygame.mouse.get_pressed()[0]:
            spread = SPREAD_BASE + self.recoil * SPREAD_RECOIL_SCALE
            self.fire_hitscan(self.player, spread)
            if self.player.fire_cd > FIRE_COOLDOWN * 0.99:
                self.recoil = clamp(self.recoil + RECOIL_KICK, 0.0, 1.0)
                self.player.angle = wrap_angle(self.player.angle + random.uniform(-RECOIL_JITTER, RECOIL_JITTER) * self.recoil)

        self.move(self.player, dt)

    def enemy_move_vector(self, e, to_p, has_los):
        if has_los and to_p.length_squared() > 1e-4:
            e.last_seen = pygame.Vector2(self.player.pos)
            base = to_p.normalize()
        elif e.last_seen is not None:
            to_last = e.last_seen - e.pos
            if to_last.length_squared() > 64:
                base = to_last.normalize()
            else:
                base = pygame.Vector2(0, 0)
                e.last_seen = None
        else:
            base = pygame.Vector2(0, 0)

        if base.length_squared() == 0:
            return base

        e.repath_t -= 1 / FPS
        if e.repath_t <= 0:
            e.repath_t = random.uniform(0.3, 0.8)
            if random.random() < 0.35:
                e.strafe_pref *= -1

        right = pygame.Vector2(-base.y, base.x)
        candidates = [
            base,
            (base + right * 0.65 * e.strafe_pref),
            (base - right * 0.65 * e.strafe_pref),
            (base + right * 0.45),
            (base - right * 0.45),
        ]

        best = base
        best_score = -1e9
        for c in candidates:
            if c.length_squared() == 0:
                continue
            c = c.normalize()
            probe = e.pos + c * 30
            if self.circle_wall(probe, e.radius):
                continue

            score = c.dot(base)
            if not has_los:
                score += 0.1 * abs(c.dot(right))

            if score > best_score:
                best_score = score
                best = c

        avoid = pygame.Vector2(0, 0)
        for other in self.enemies:
            if other is e or other.dead:
                continue
            delta = e.pos - other.pos
            d2 = delta.length_squared()
            if d2 < ENEMY_SEPARATION * ENEMY_SEPARATION and d2 > 1:
                avoid += delta.normalize() * 0.8

        move_vec = best + avoid
        if move_vec.length_squared() > 0:
            move_vec = move_vec.normalize()
        return move_vec

    def update_enemies(self, dt):
        for e in self.enemies:
            if e.dead:
                continue

            to_p = self.player.pos - e.pos
            dist = to_p.length()
            has_los = self.has_los(e.pos, self.player.pos)

            e.vel = pygame.Vector2(0, 0)
            if dist > 165:
                move_vec = self.enemy_move_vector(e, to_p, has_los)
                e.vel = move_vec * ENEMY_SPEED

            if dist > 0:
                e.angle = math.atan2(to_p.y, to_p.x)

            self.move(e, dt)

            if has_los and dist < 540 and random.random() < dt * 4.0:
                self.fire_hitscan(e, spread=0.03)

    def end_round(self, winner, text):
        if self.state == "ended":
            return
        self.state = "ended"
        self.end_text = text
        self.end_timer = 3.0
        if winner == "CT":
            self.score_ct += 1
        else:
            self.score_t += 1

    def update_objective(self, dt):
        if self.state != "live":
            return

        k = pygame.key.get_pressed()
        in_site = (self.player.pos - self.site).length() <= SITE_R

        if not self.bomb_planted:
            if in_site and k[pygame.K_e] and not self.player.dead:
                self.progress += dt
                if self.progress >= PLANT_TIME:
                    self.bomb_planted = True
                    self.progress = 0.0
                    self.feed.append("Bomb planted")
            else:
                self.progress = max(0.0, self.progress - dt * 1.5)
        else:
            self.bomb -= dt
            alive_ct = [e for e in self.enemies if not e.dead]
            near = any((e.pos - self.site).length() <= SITE_R for e in alive_ct)
            if near and random.random() < dt * 0.55:
                self.progress += dt
                if self.progress >= DEFUSE_TIME:
                    self.end_round("CT", "CT defused the bomb")
            else:
                self.progress = max(0.0, self.progress - dt)
            if self.bomb <= 0:
                self.end_round("T", "Bomb exploded")

    def update_round(self, dt):
        if self.state == "buy":
            self.buy -= dt
            if self.buy <= 0:
                self.state = "live"
                self.feed.append("Round live")
        elif self.state == "live":
            self.round_time -= dt
            if self.round_time <= 0 and not self.bomb_planted:
                self.end_round("CT", "CT won (time)")
        else:
            self.end_timer -= dt
            if self.end_timer <= 0:
                self.reset_round()

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if ev.key == pygame.K_TAB:
                    self.mouse_captured = not self.mouse_captured
                    pygame.event.set_grab(self.mouse_captured)
                    pygame.mouse.set_visible(not self.mouse_captured)
                    pygame.mouse.get_rel()

                if (
                    ev.key == pygame.K_r
                    and self.player.reloading <= 0
                    and self.player.mag < MAG_SIZE
                    and self.player.reserve > 0
                ):
                    self.player.reloading = RELOAD_TIME

    def update(self, dt):
        self.handle_events()

        for a in [self.player] + self.enemies:
            if a.fire_cd > 0:
                a.fire_cd -= dt
            if a.reloading > 0:
                a.reloading -= dt
                if a.reloading <= 0:
                    need = MAG_SIZE - a.mag
                    take = min(need, a.reserve)
                    a.mag += take
                    a.reserve -= take

        for t in self.tracers:
            t.update(dt)
        self.tracers = [t for t in self.tracers if t.alive]

        self.recoil = max(0.0, self.recoil - dt * RECOIL_RECOVERY)

        self.update_round(dt)
        if self.state == "live":
            self.update_player(dt)
            self.update_enemies(dt)
            self.update_objective(dt)

            alive_ct = [e for e in self.enemies if not e.dead]
            if self.player.dead:
                self.end_round("CT", "CT won (you died)")
            elif not alive_ct and not self.bomb_planted:
                self.end_round("T", "T won (all CT eliminated)")

        if len(self.feed) > 8:
            self.feed = self.feed[-8:]

    def render_walls(self):
        self.depth_buffer = [MAX_DEPTH] * WIDTH

        for x in range(WIDTH):
            cam_x = (2.0 * x / WIDTH) - 1.0
            ray_angle = self.player.angle + math.atan(cam_x * math.tan(HALF_FOV))
            dist, side, hit_x, hit_y = self.cast_ray(self.player.pos, ray_angle)

            corrected = max(0.001, dist * math.cos(ray_angle - self.player.angle))
            self.depth_buffer[x] = corrected

            line_h = int((CELL * PROJ_PLANE) / corrected)
            y0 = HEIGHT // 2 - line_h // 2
            y1 = HEIGHT // 2 + line_h // 2

            base = 185 - int(min(145, corrected * 0.09))
            if side == 1:
                base = int(base * 0.78)

            checker = int((hit_x + hit_y) / 32) % 2
            if checker:
                wall_col = (base, int(base * 0.95), int(base * 0.88))
            else:
                wall_col = (int(base * 0.92), int(base * 0.9), int(base * 0.85))

            pygame.draw.line(self.screen, wall_col, (x, y0), (x, y1))

    def render_sprite(self, pos, radius, color, y_offset=0.0):
        rel = pos - self.player.pos
        dist = rel.length()
        if dist <= 1e-4:
            return

        ang = wrap_angle(math.atan2(rel.y, rel.x) - self.player.angle)
        if abs(ang) > FOV * 0.62:
            return

        screen_x = int((0.5 + ang / FOV) * WIDTH)
        size = int((radius * 2 * PROJ_PLANE) / dist)
        if size <= 1:
            return

        x0 = screen_x - size // 2
        x1 = screen_x + size // 2
        y0 = HEIGHT // 2 - size // 2 + int(y_offset)
        y1 = y0 + size

        shade = clamp(255 - int(dist * 0.22), 45, 255)
        sprite_col = (
            int(color[0] * (shade / 255.0)),
            int(color[1] * (shade / 255.0)),
            int(color[2] * (shade / 255.0)),
        )

        for sx in range(max(0, x0), min(WIDTH, x1)):
            if dist >= self.depth_buffer[sx]:
                continue
            pygame.draw.line(self.screen, sprite_col, (sx, y0), (sx, y1))

    def render_tracers(self):
        for t in self.tracers:
            mid = (t.start + t.end) * 0.5
            rel = mid - self.player.pos
            dist = rel.length()
            if dist < 30 or dist > 1000:
                continue

            ang = wrap_angle(math.atan2(rel.y, rel.x) - self.player.angle)
            if abs(ang) > HALF_FOV:
                continue

            sx = int((0.5 + ang / FOV) * WIDTH)
            if 0 <= sx < WIDTH and dist < self.depth_buffer[sx]:
                col = (255, 225, 155) if t.team == "T" else (255, 135, 135)
                glow = clamp(int(255 * (t.life / 0.08)), 30, 255)
                col = (int(col[0] * glow / 255), int(col[1] * glow / 255), int(col[2] * glow / 255))
                y = int(HEIGHT * 0.52)
                pygame.draw.line(self.screen, col, (sx, y - 7), (sx, y + 7), 2)

    def render_site_beacon(self):
        rel = self.site - self.player.pos
        dist = rel.length()
        if dist < 1:
            return

        ang = wrap_angle(math.atan2(rel.y, rel.x) - self.player.angle)
        if abs(ang) > HALF_FOV * 1.05:
            return

        sx = int((0.5 + ang / FOV) * WIDTH)
        if sx < 0 or sx >= WIDTH:
            return

        if dist >= self.depth_buffer[sx] + 4:
            return

        pulse = 0.65 + 0.35 * abs(math.sin(pygame.time.get_ticks() * 0.008))
        base_h = int((SITE_R * PROJ_PLANE / max(1.0, dist)) * 1.35)
        core_h = int(base_h * pulse)
        cy = HEIGHT // 2

        if self.bomb_planted:
            col = (255, 65, 65)
            glow = (255, 130, 90)
        else:
            col = (240, 185, 70)
            glow = (255, 220, 130)

        pygame.draw.line(self.screen, glow, (sx, cy - base_h), (sx, cy + base_h), 3)
        pygame.draw.line(self.screen, col, (sx, cy - core_h), (sx, cy + core_h), 5)

    def draw_minimap(self):
        scale = 0.20
        mini_w = int(MAP_W * CELL * scale)
        mini_h = int(MAP_H * CELL * scale)
        surf = pygame.Surface((mini_w + 2, mini_h + 2), pygame.SRCALPHA)
        surf.fill((10, 12, 16, 190))

        for gy in range(MAP_H):
            for gx in range(MAP_W):
                if MAP_GRID[gy][gx] != "#":
                    continue
                rx = int(gx * CELL * scale)
                ry = int(gy * CELL * scale)
                rs = int(CELL * scale)
                pygame.draw.rect(surf, (95, 105, 118, 235), (rx, ry, rs, rs))

        site_pos = (int(self.site.x * scale), int(self.site.y * scale))
        site_col = (250, 80, 80) if self.bomb_planted else (230, 175, 80)
        pygame.draw.circle(surf, site_col, site_pos, max(2, int(SITE_R * scale * 0.32)), 1)

        for e in self.enemies:
            if e.dead:
                continue
            ep = (int(e.pos.x * scale), int(e.pos.y * scale))
            pygame.draw.circle(surf, (100, 190, 240), ep, 3)

        pp = (int(self.player.pos.x * scale), int(self.player.pos.y * scale))
        pygame.draw.circle(surf, (255, 155, 95), pp, 4)
        look_end = (
            int(pp[0] + math.cos(self.player.angle) * 14),
            int(pp[1] + math.sin(self.player.angle) * 14),
        )
        pygame.draw.line(surf, (255, 240, 220), pp, look_end, 2)

        self.screen.blit(surf, (WIDTH - surf.get_width() - 16, HEIGHT - surf.get_height() - 16))
        self.screen.blit(self.small.render("MINIMAP", True, (220, 228, 236)), (WIDTH - surf.get_width() - 12, HEIGHT - surf.get_height() - 34))

    def draw_hud(self):
        score = self.big.render(f"CT {self.score_ct}  -  {self.score_t} T", True, (235, 238, 242))
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, 12))

        state = (
            f"Buy: {self.buy:0.1f}s"
            if self.state == "buy"
            else (f"Round: {max(0, self.round_time):0.1f}s" if self.state == "live" else "Round ended")
        )
        self.screen.blit(self.font.render(state, True, (220, 228, 236)), (24, 18))

        hp_col = (140, 255, 160) if self.player.hp > 35 else (255, 120, 120)
        self.screen.blit(self.font.render(f"HP {self.player.hp}", True, hp_col), (24, HEIGHT - 78))
        self.screen.blit(
            self.font.render(f"Ammo {self.player.mag}/{self.player.reserve}", True, (240, 220, 160)),
            (140, HEIGHT - 78),
        )

        if self.player.reloading > 0:
            self.screen.blit(self.font.render("Reloading...", True, (255, 210, 130)), (24, HEIGHT - 105))

        if self.bomb_planted:
            bt = self.font.render(f"Bomb: {max(0, self.bomb):0.1f}s", True, (255, 120, 120))
            self.screen.blit(bt, (WIDTH - bt.get_width() - 24, 18))

        y = 60
        for t in self.feed:
            txt = self.font.render(t, True, (208, 216, 225))
            self.screen.blit(txt, (WIDTH - txt.get_width() - 20, y))
            y += 22

        gap = 8 + int(self.recoil * 22)
        cx, cy = WIDTH // 2, HEIGHT // 2
        pygame.draw.line(self.screen, (255, 255, 255), (cx - (gap + 7), cy), (cx - gap, cy), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (cx + gap, cy), (cx + (gap + 7), cy), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (cx, cy - (gap + 7)), (cx, cy - gap), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (cx, cy + gap), (cx, cy + (gap + 7)), 2)

        if self.progress > 0:
            total = PLANT_TIME if not self.bomb_planted else DEFUSE_TIME
            ratio = clamp(self.progress / total, 0.0, 1.0)
            bw, bh = 260, 16
            bx = WIDTH // 2 - bw // 2
            by = HEIGHT - 56
            pygame.draw.rect(self.screen, (20, 20, 24), (bx, by, bw, bh), border_radius=4)
            pygame.draw.rect(self.screen, (235, 180, 90), (bx, by, int(bw * ratio), bh), border_radius=4)

        if self.state == "ended":
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 130))
            self.screen.blit(ov, (0, 0))
            t = self.big.render(self.end_text, True, (255, 255, 255))
            self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 24))

        controls = self.font.render(
            "WASD move | Mouse look/shoot | R reload | E plant | Shift walk | TAB free mouse",
            True,
            (198, 206, 214),
        )
        self.screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT - 28))

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (75, 98, 132), (0, 0, WIDTH, HEIGHT // 2))
        pygame.draw.rect(self.screen, (58, 54, 48), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

        self.render_walls()

        for e in sorted(self.enemies, key=lambda x: (x.pos - self.player.pos).length(), reverse=True):
            if e.dead:
                continue
            self.render_sprite(e.pos, e.radius * 2.2, (90, 170, 220))

        self.render_site_beacon()
        self.render_tracers()
        self.draw_hud()
        self.draw_minimap()
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
