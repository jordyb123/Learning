namespace Day3;

using System;

public class Program
{
    static void Main()
    {
        int hp = 100;

        PrintHP(hp);

        hp = Damage(hp, 30);    
        PrintHP(hp);

        Attack();
        Attack(15);
        Attack(25, "Heavy");
    }
    static void PrintHP(int hp)
    {
        Console.WriteLine("HP: " + hp);
    }

    static int Damage(int hp, int amount)
    {
        return hp - amount;
    }

    static int Heal(int hp, int amount)
    {
        return hp + amount;
    }

    static void Attack()
    {
        Console.WriteLine("Basic attack");
    }

    static void Attack(int damage)
    {
        Console.WriteLine("Attack for " + damage);
    }

    static void Attack(int damage, string type)
    {
        Console.WriteLine(type + " attack for " + damage);
    }

}

