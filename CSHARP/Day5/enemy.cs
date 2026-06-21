using System;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        Enemies inv = new Enemies();

        Enemy gargoyle = new Enemy("Gargoyle", EnemyType.Flying,
        new Dictionary<string, int>()
        {
            {"damage", 10 },
            {"hp", 100 }
        }
        );

        Enemy grunt = new Enemy("Grunt", EnemyType.Boss,
        new Dictionary<string, int>()
        {
            {"damage", 100 },
            {"hp", 10000 }
        }
        );

        inv.AddEnemy(gargoyle);
        inv.AddEnemy(grunt);
        inv.PrintInventory();
    }
}

public enum EnemyType
        {
            Flying,
            Ground,
            Boss
        }

public class Enemy
{
    public string name;
    public EnemyType type;
    public Dictionary<string, int> stats;

    public Enemy(string name, EnemyType type, Dictionary<string, int> stats)
    {
        this.name = name;
        this.type = type;
        this.stats = stats;
    }
}

public class Enemies
{
    public List<Enemy> enemies = new List<Enemy>();

    public void AddEnemy(Enemy enemy)
    {
        enemies.Add(enemy);
    }

    public void PrintInventory()
    {
        foreach (Enemy enemy in enemies)
        {
            Console.WriteLine(enemy.name + " (" + enemy.type + ")");

            foreach (var stat in enemy.stats)
            {
                Console.WriteLine(" " + stat.Key + ": " + stat.Value);
            }

            Console.WriteLine();
        }
    }
}