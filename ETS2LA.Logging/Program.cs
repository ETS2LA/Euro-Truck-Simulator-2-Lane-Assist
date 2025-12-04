using Serilog;
using Serilog.Sinks.SystemConsole.Themes;

namespace ETS2LA.Logging
{
    public class Logger
    {
        private static readonly ILogger _logger;

        static Logger()
        {
            _logger = new LoggerConfiguration()
                .WriteTo.Console(theme: AnsiConsoleTheme.Code)
                .CreateLogger();
        }

        public static void Debug(string message)
        {
            _logger.Debug(message);
        }
        public static void Info(string message)
        {
            _logger.Information(message);
        }

        public static void Warn(string message)
        {
            _logger.Warning(message);
        }

        public static void Error(string message)
        {
            _logger.Error(message);
        }
    }
}