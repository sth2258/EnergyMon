using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading;

namespace EnergyMonitor
{
    class Program
    {
        static void Main(string[] args)
        {
            while (true)
            {
                RunPython();
                Thread.Sleep(2000);
            }
            

            Console.WriteLine("Press any key to continue...");


            Console.ReadKey(true);
        }
        public static string Base64Encode(string plainText)
        {
            var plainTextBytes = System.Text.Encoding.UTF8.GetBytes(plainText);
            return System.Convert.ToBase64String(plainTextBytes);
        }
        
        public static void RunPython()
        {
            var process = new Process()
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "py",
                    Arguments = "python" + Path.DirectorySeparatorChar + "energyMonitor.py 'steve.t.haber+vesync@gmail.com' '" + Base64Encode("cSG__(\"Fp5rb-895") + "'",
                    RedirectStandardOutput = true,

                    UseShellExecute = false,
                    CreateNoWindow = false,
                }
            };
            process.Start();
            string result = process.StandardOutput.ReadToEnd();
            //string sub1 = result.Substring(result.IndexOf("Power"));
            //string sub2 = sub1.Substring(0, sub1.IndexOf("Watts")+5);
            //Console.WriteLine(sub2);
            process.WaitForExit();
            JArray obja = (JArray)JsonConvert.DeserializeObject(result);
            Console.WriteLine(obja[2].Last);
        }
    }
    
}
