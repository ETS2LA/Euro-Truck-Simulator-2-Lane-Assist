using System;
using ETS2LA.Shared;

namespace ETS2LA.Backend
{
    public static class Program
    {
        static EventBus _bus = new EventBus();

        static void Main(string[] args)
        {
            Console.WriteLine("ETS2LA Application Started.");
        }
    }
}