using System;
using System.Security;

class Program
{
    static void Main()
    {
        int hp = 30;

        //Loop until hp = 0
        while (hp > 0)
        {
            hp -= 5;

            if (hp <= 0)
            {
                Console.WriteLine("Player Died");
            }
            else if (hp < 20)
            {
                Console.WriteLine("Low HP: " + hp);
            }
            else
            {
                Console.WriteLine("HP: " + hp);
            }
        }

        // Switch example
        string state = "Attack";

        switch (state)
        {
            case "Idle":
                Console.WriteLine("Player is idle");
                break;

            case "Run":
                Console.WriteLine("Player is attacking");
                break;

            case "Attack":
                Console.WriteLine("Player is attacking");
                break;

            default:
                Console.WriteLine("Unknown state");
                break;
        }
    }
}