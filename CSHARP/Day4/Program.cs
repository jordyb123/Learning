class Program
{
    static void Main()
    {
        Player p = new Player(100, 20);
        Enemy e = new Enemy(50);

        p.Attack(e);

        Console.WriteLine("Enemy HP after attack: " + e.hp);
    }
}

public class Player
{
    public int hp;
    public int maxHp;
    public int damage;

    public Player(int hp, int damage)
    {
        this.hp = hp;
        this.maxHp = hp;
        this.damage = damage;
    }

    public void TakeDamage(int amount)
    {
        hp -= amount;

        if (hp < 0)
            hp = 0;
    }

    public void Heal(int amount)
    {
        hp += amount;

        if (hp > maxHp)
            hp = maxHp;
    }

    public void Attack(Enemy target)
    {
        target.TakeDamage(damage);
    }
}

public class Enemy
{

    public int hp;

    public Enemy(int hp)
    {
        this.hp = hp;
    }

    public void TakeDamage(int amount)
    {
        hp -= amount;
    }
}