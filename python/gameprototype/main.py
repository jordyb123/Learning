import math
import random
import sys

import pygame


# CS2-inspired top-down prototype made with pygame.
# Controls:
# - WASD: Move
# - Mouse: Aim
# - Left click: Shoot
# - R: Reload
# - E: Plant/defuse bomb at site
# - Shift: Walk (quieter/slower)


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

MAP_PADDING = 40
SITE_RADIUS = 70

PLAYER_SPEED = 260
WALK_SPEED_MULTIPLIER = 0.58
PLAYER_RADIUS = 16
PLAYER_HP = 100

ENEMY_RADIUS = 15
ENEMY_SPEED = 150
ENEMY_HP = 65

BULLET_SPEED = 850
FIRE_COOLDOWN = 0.12
BULLET_DAMAGE = 32
BULLET_MAX_DISTANCE = 760

MAGAZINE_SIZE = 20
RESERVE_AMMO = 100
RELOAD_TIME = 1.6

ROUND_TIME = 95.0
BUY_TIME = 8.0
BOMB_PLANT_TIME = 2.8
BOMB_DEFUSE_TIME = 4.5
BOMB_EXPLODE_TIME = 30.0

TEAM_CT = "CT"
TEAM_T = "T"


def clamp(value, lo, hi):
	return max(lo, min(hi, value))


def vec_from_angle(angle):
	return pygame.Vector2(math.cos(angle), math.sin(angle))


class Bullet:
	def __init__(self, pos, direction, team):
		self.pos = pygame.Vector2(pos)
		self.prev_pos = pygame.Vector2(pos)
		self.direction = pygame.Vector2(direction)
		self.team = team
		self.distance_traveled = 0.0
		self.alive = True

	def update(self, dt):
		self.prev_pos = self.pos.copy()
		step = self.direction * BULLET_SPEED * dt
		self.pos += step
		self.distance_traveled += step.length()
		if self.distance_traveled >= BULLET_MAX_DISTANCE:
			self.alive = False


class Fighter:
	def __init__(self, team, pos, is_player=False):
		self.team = team
		self.pos = pygame.Vector2(pos)
		self.vel = pygame.Vector2(0, 0)
		self.radius = PLAYER_RADIUS if is_player else ENEMY_RADIUS
		self.hp = PLAYER_HP if is_player else ENEMY_HP
		self.is_player = is_player

		self.facing_angle = 0.0
		self.fire_timer = 0.0
		self.reload_timer = 0.0

		self.mag_ammo = MAGAZINE_SIZE
		self.reserve_ammo = RESERVE_AMMO
		self.is_reloading = False

		self.dead = False

	def can_shoot(self):
		return (not self.dead) and (not self.is_reloading) and self.mag_ammo > 0 and self.fire_timer <= 0.0

	def take_damage(self, dmg):
		if self.dead:
			return
		self.hp -= dmg
		if self.hp <= 0:
			self.hp = 0
			self.dead = True

	def start_reload(self):
		if self.dead:
			return
		if self.is_reloading:
			return
		if self.mag_ammo >= MAGAZINE_SIZE:
			return
		if self.reserve_ammo <= 0:
			return
		self.is_reloading = True
		self.reload_timer = RELOAD_TIME

	def update_reload(self, dt):
		if not self.is_reloading:
			return
		self.reload_timer -= dt
		if self.reload_timer <= 0.0:
			needed = MAGAZINE_SIZE - self.mag_ammo
			take = min(needed, self.reserve_ammo)
			self.mag_ammo += take
			self.reserve_ammo -= take
			self.is_reloading = False


class Game:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("CS2 Prototype - pygame")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()

		self.font_small = pygame.font.SysFont("consolas", 18)
		self.font_med = pygame.font.SysFont("consolas", 28)
		self.font_big = pygame.font.SysFont("consolas", 48, bold=True)

		self.walls = self._build_map_walls()
		self.site_pos = pygame.Vector2(SCREEN_WIDTH * 0.76, SCREEN_HEIGHT * 0.42)

		self.score_ct = 0
		self.score_t = 0

		self.round_state = "buy"
		self.round_timer = ROUND_TIME
		self.buy_timer = BUY_TIME

		self.bomb_planted = False
		self.bomb_timer = BOMB_EXPLODE_TIME
		self.bomb_progress = 0.0
		self.planting = False
		self.defusing = False

		self.kill_feed = []
		self.round_end_text = ""
		self.round_end_timer = 0.0

		self.player = None
		self.enemies = []
		self.bullets = []

		self.reset_round()

	def _build_map_walls(self):
		return [
			pygame.Rect(260, 140, 40, 380),
			pygame.Rect(430, 100, 40, 270),
			pygame.Rect(430, 430, 40, 210),
			pygame.Rect(620, 210, 48, 300),
			pygame.Rect(840, 110, 42, 270),
			pygame.Rect(960, 350, 42, 260),
			pygame.Rect(1020, 220, 180, 42),
			pygame.Rect(1000, 500, 180, 42),
		]

	def spawn_enemy(self):
		# Spawn at random points on the right side while avoiding wall overlap.
		for _ in range(50):
			x = random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - MAP_PADDING - ENEMY_RADIUS)
			y = random.randint(MAP_PADDING + ENEMY_RADIUS, SCREEN_HEIGHT - MAP_PADDING - ENEMY_RADIUS)
			p = pygame.Vector2(x, y)
			if not self._circle_hits_wall(p, ENEMY_RADIUS):
				return Fighter(TEAM_CT, p, is_player=False)
		return Fighter(TEAM_CT, pygame.Vector2(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2), is_player=False)

	def reset_round(self):
		self.player = Fighter(TEAM_T, pygame.Vector2(120, SCREEN_HEIGHT // 2), is_player=True)
		self.enemies = [self.spawn_enemy() for _ in range(5)]
		self.bullets = []

		self.round_state = "buy"
		self.buy_timer = BUY_TIME
		self.round_timer = ROUND_TIME

		self.bomb_planted = False
		self.bomb_timer = BOMB_EXPLODE_TIME
		self.bomb_progress = 0.0
		self.planting = False
		self.defusing = False

		self.round_end_text = ""
		self.round_end_timer = 0.0
		self.kill_feed.clear()

	def _circle_hits_wall(self, center, radius):
		probe = pygame.Rect(center.x - radius, center.y - radius, radius * 2, radius * 2)
		for wall in self.walls:
			if wall.colliderect(probe):
				return True
		return False

	def _move_with_collisions(self, fighter, dt):
		fighter.pos.x += fighter.vel.x * dt
		fighter.pos.x = clamp(fighter.pos.x, MAP_PADDING + fighter.radius, SCREEN_WIDTH - MAP_PADDING - fighter.radius)
		if self._circle_hits_wall(fighter.pos, fighter.radius):
			fighter.pos.x -= fighter.vel.x * dt

		fighter.pos.y += fighter.vel.y * dt
		fighter.pos.y = clamp(fighter.pos.y, MAP_PADDING + fighter.radius, SCREEN_HEIGHT - MAP_PADDING - fighter.radius)
		if self._circle_hits_wall(fighter.pos, fighter.radius):
			fighter.pos.y -= fighter.vel.y * dt

	def _line_hits_wall(self, p0, p1):
		for wall in self.walls:
			if wall.clipline(p0, p1):
				return True
		return False

	def fire_from(self, shooter):
		if not shooter.can_shoot():
			return
		shooter.mag_ammo -= 1
		shooter.fire_timer = FIRE_COOLDOWN

		spread = random.uniform(-0.04, 0.04)
		direction = vec_from_angle(shooter.facing_angle + spread)
		start = shooter.pos + direction * (shooter.radius + 6)
		self.bullets.append(Bullet(start, direction, shooter.team))

	def _update_player(self, dt):
		keys = pygame.key.get_pressed()
		move = pygame.Vector2(0, 0)

		if keys[pygame.K_w]:
			move.y -= 1
		if keys[pygame.K_s]:
			move.y += 1
		if keys[pygame.K_a]:
			move.x -= 1
		if keys[pygame.K_d]:
			move.x += 1

		speed = PLAYER_SPEED
		if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
			speed *= WALK_SPEED_MULTIPLIER

		if move.length_squared() > 0:
			move = move.normalize() * speed
		self.player.vel = move

		mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
		look = mouse_pos - self.player.pos
		if look.length_squared() > 0:
			self.player.facing_angle = math.atan2(look.y, look.x)

		if pygame.mouse.get_pressed()[0]:
			self.fire_from(self.player)

		self._move_with_collisions(self.player, dt)

	def _update_enemies(self, dt):
		living_enemies = [e for e in self.enemies if not e.dead]
		for enemy in living_enemies:
			to_player = self.player.pos - enemy.pos
			dist = to_player.length()

			enemy.vel = pygame.Vector2(0, 0)
			if dist > 190:
				enemy.vel = to_player.normalize() * ENEMY_SPEED

			if dist > 0:
				enemy.facing_angle = math.atan2(to_player.y, to_player.x)

			self._move_with_collisions(enemy, dt)

			if dist < 470 and random.random() < dt * 4.8:
				if not self._line_hits_wall(enemy.pos, self.player.pos):
					self.fire_from(enemy)

	def _update_bullets(self, dt):
		for bullet in self.bullets:
			if not bullet.alive:
				continue
			bullet.update(dt)

			if bullet.pos.x < 0 or bullet.pos.x > SCREEN_WIDTH or bullet.pos.y < 0 or bullet.pos.y > SCREEN_HEIGHT:
				bullet.alive = False
				continue

			if self._line_hits_wall(bullet.prev_pos, bullet.pos):
				bullet.alive = False
				continue

			if bullet.team == TEAM_T:
				for enemy in self.enemies:
					if enemy.dead:
						continue
					if (enemy.pos - bullet.pos).length_squared() <= (enemy.radius + 2) ** 2:
						enemy.take_damage(BULLET_DAMAGE)
						bullet.alive = False
						if enemy.dead:
							self.kill_feed.append("You eliminated a CT")
						break
			else:
				if not self.player.dead:
					if (self.player.pos - bullet.pos).length_squared() <= (self.player.radius + 2) ** 2:
						self.player.take_damage(BULLET_DAMAGE)
						bullet.alive = False
						if self.player.dead:
							self.kill_feed.append("You were eliminated")

		self.bullets = [b for b in self.bullets if b.alive]

	def _update_objective(self, dt):
		dist_to_site = (self.player.pos - self.site_pos).length()
		in_site = dist_to_site <= SITE_RADIUS
		e_pressed = pygame.key.get_pressed()[pygame.K_e]

		self.planting = False
		self.defusing = False

		if self.round_state != "live":
			return

		if not self.bomb_planted:
			if in_site and e_pressed and not self.player.dead:
				self.planting = True
				self.bomb_progress += dt
				if self.bomb_progress >= BOMB_PLANT_TIME:
					self.bomb_planted = True
					self.bomb_progress = 0.0
					self.kill_feed.append("Bomb planted")
			else:
				self.bomb_progress = max(0.0, self.bomb_progress - dt * 1.5)
		else:
			closest_enemy = None
			closest_dist = 999999.0
			for enemy in self.enemies:
				if enemy.dead:
					continue
				d = (enemy.pos - self.site_pos).length()
				if d < closest_dist:
					closest_dist = d
					closest_enemy = enemy

			if closest_enemy and closest_dist <= SITE_RADIUS and random.random() < dt * 0.55:
				self.defusing = True
				self.bomb_progress += dt
				if self.bomb_progress >= BOMB_DEFUSE_TIME:
					self.end_round(TEAM_CT, "CT defused the bomb")
			else:
				self.bomb_progress = max(0.0, self.bomb_progress - dt)

			self.bomb_timer -= dt
			if self.bomb_timer <= 0.0:
				self.end_round(TEAM_T, "Bomb exploded")

	def end_round(self, winner, message):
		if self.round_state == "ended":
			return
		self.round_state = "ended"
		self.round_end_timer = 3.2
		self.round_end_text = message
		if winner == TEAM_CT:
			self.score_ct += 1
		else:
			self.score_t += 1

	def _check_round_win_conditions(self):
		if self.round_state != "live":
			return

		alive_enemies = [e for e in self.enemies if not e.dead]

		if self.player.dead:
			self.end_round(TEAM_CT, "CT won (you died)")
			return

		if not alive_enemies and not self.bomb_planted:
			self.end_round(TEAM_T, "T won (all CT eliminated)")
			return

		if self.round_timer <= 0.0 and not self.bomb_planted:
			self.end_round(TEAM_CT, "CT won (time)")

	def _update_round_state(self, dt):
		if self.round_state == "buy":
			self.buy_timer -= dt
			if self.buy_timer <= 0:
				self.round_state = "live"
				self.kill_feed.append("Round live")
		elif self.round_state == "live":
			self.round_timer -= dt
		elif self.round_state == "ended":
			self.round_end_timer -= dt
			if self.round_end_timer <= 0:
				self.reset_round()

	def update(self, dt):
		self._update_round_state(dt)

		if self.player.fire_timer > 0:
			self.player.fire_timer -= dt
		self.player.update_reload(dt)

		for enemy in self.enemies:
			if enemy.fire_timer > 0:
				enemy.fire_timer -= dt
			enemy.update_reload(dt)
			if not enemy.dead and enemy.mag_ammo <= 0:
				enemy.start_reload()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == pygame.K_r:
					self.player.start_reload()

		if self.round_state == "live":
			self._update_player(dt)
			self._update_enemies(dt)
			self._update_bullets(dt)
			self._update_objective(dt)
			self._check_round_win_conditions()

		if len(self.kill_feed) > 6:
			self.kill_feed = self.kill_feed[-6:]

	def _draw_grid(self):
		self.screen.fill((16, 22, 30))
		grid_color = (24, 34, 44)
		for x in range(0, SCREEN_WIDTH, 40):
			pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
		for y in range(0, SCREEN_HEIGHT, 40):
			pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

	def draw(self):
		self._draw_grid()

		pygame.draw.rect(
			self.screen,
			(35, 54, 73),
			(MAP_PADDING, MAP_PADDING, SCREEN_WIDTH - MAP_PADDING * 2, SCREEN_HEIGHT - MAP_PADDING * 2),
			border_radius=10,
		)

		for wall in self.walls:
			pygame.draw.rect(self.screen, (77, 96, 110), wall, border_radius=4)

		pygame.draw.circle(self.screen, (120, 80, 40), (int(self.site_pos.x), int(self.site_pos.y)), SITE_RADIUS, 3)

		if self.bomb_planted:
			pulse = int(120 + 80 * abs(math.sin(pygame.time.get_ticks() * 0.012)))
			pygame.draw.circle(self.screen, (pulse, 40, 40), (int(self.site_pos.x), int(self.site_pos.y)), 11)

		for bullet in self.bullets:
			pygame.draw.circle(self.screen, (255, 226, 150), (int(bullet.pos.x), int(bullet.pos.y)), 3)

		for enemy in self.enemies:
			if enemy.dead:
				pygame.draw.circle(self.screen, (80, 70, 70), (int(enemy.pos.x), int(enemy.pos.y)), enemy.radius)
				continue

			pygame.draw.circle(self.screen, (90, 170, 220), (int(enemy.pos.x), int(enemy.pos.y)), enemy.radius)
			end = enemy.pos + vec_from_angle(enemy.facing_angle) * (enemy.radius + 10)
			pygame.draw.line(self.screen, (220, 245, 255), enemy.pos, end, 2)

		if self.player.dead:
			color = (120, 70, 70)
		else:
			color = (220, 145, 90)
		pygame.draw.circle(self.screen, color, (int(self.player.pos.x), int(self.player.pos.y)), self.player.radius)
		end = self.player.pos + vec_from_angle(self.player.facing_angle) * (self.player.radius + 12)
		pygame.draw.line(self.screen, (255, 238, 220), self.player.pos, end, 3)

		mouse_pos = pygame.mouse.get_pos()
		pygame.draw.circle(self.screen, (245, 245, 245), mouse_pos, 10, 1)
		pygame.draw.line(self.screen, (245, 245, 245), (mouse_pos[0] - 6, mouse_pos[1]), (mouse_pos[0] + 6, mouse_pos[1]), 1)
		pygame.draw.line(self.screen, (245, 245, 245), (mouse_pos[0], mouse_pos[1] - 6), (mouse_pos[0], mouse_pos[1] + 6), 1)

		self.draw_hud()
		pygame.display.flip()

	def draw_hud(self):
		score_text = self.font_big.render(f"CT {self.score_ct}  -  {self.score_t} T", True, (234, 236, 240))
		self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 12))

		if self.round_state == "buy":
			state = f"Buy phase: {self.buy_timer:0.1f}s"
		elif self.round_state == "live":
			state = f"Round: {max(0, self.round_timer):0.1f}s"
		else:
			state = "Round ended"
		state_text = self.font_med.render(state, True, (223, 229, 236))
		self.screen.blit(state_text, (24, 18))

		hp_color = (120, 255, 140) if self.player.hp > 35 else (255, 120, 120)
		hp_text = self.font_med.render(f"HP {self.player.hp}", True, hp_color)
		ammo_text = self.font_med.render(f"Ammo {self.player.mag_ammo}/{self.player.reserve_ammo}", True, (240, 220, 160))
		self.screen.blit(hp_text, (26, SCREEN_HEIGHT - 72))
		self.screen.blit(ammo_text, (170, SCREEN_HEIGHT - 72))

		if self.player.is_reloading:
			rel = self.font_small.render("Reloading...", True, (255, 210, 150))
			self.screen.blit(rel, (26, SCREEN_HEIGHT - 100))

		if self.bomb_planted:
			bomb_text = self.font_med.render(f"Bomb: {max(0, self.bomb_timer):0.1f}s", True, (255, 120, 120))
			self.screen.blit(bomb_text, (SCREEN_WIDTH - bomb_text.get_width() - 24, 18))

		if self.planting:
			p = min(1.0, self.bomb_progress / BOMB_PLANT_TIME)
			pygame.draw.rect(self.screen, (40, 45, 52), (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 40, 240, 14), border_radius=5)
			pygame.draw.rect(self.screen, (215, 170, 85), (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 40, int(240 * p), 14), border_radius=5)
		if self.defusing:
			p = min(1.0, self.bomb_progress / BOMB_DEFUSE_TIME)
			pygame.draw.rect(self.screen, (40, 45, 52), (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 40, 240, 14), border_radius=5)
			pygame.draw.rect(self.screen, (120, 190, 255), (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 40, int(240 * p), 14), border_radius=5)

		y = 64
		for text in self.kill_feed[-6:]:
			t = self.font_small.render(text, True, (208, 216, 225))
			self.screen.blit(t, (SCREEN_WIDTH - t.get_width() - 20, y))
			y += 20

		if self.round_state == "ended":
			overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 120))
			self.screen.blit(overlay, (0, 0))
			text = self.font_big.render(self.round_end_text, True, (255, 255, 255))
			self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

		controls = self.font_small.render("WASD move | Mouse aim/shoot | R reload | E plant/defuse | Shift walk", True, (196, 204, 212))
		self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, SCREEN_HEIGHT - 24))

	def run(self):
		while True:
			dt = self.clock.tick(FPS) / 1000.0
			self.update(dt)
			self.draw()


if __name__ == "__main__":
	Game().run()
