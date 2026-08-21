using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Localization;

namespace ETS2LA.Translations;

public class Language
{
    public string EnglishName { get; set; } = string.Empty;
    public string NativeName { get; set; } = string.Empty;
    public string Code { get; set; } = string.Empty;
}

public static class Languages
{    
    public static List<Language> SupportedLanguages = new List<Language>
    {
        new Language { EnglishName = "English", NativeName = "English", Code = "en" }
    };
}


public static class T
{
    private static IStringLocalizer? _localizer;

    public static void Initialize(IServiceProvider provider)
    {
        var factory = provider.GetRequiredService<IStringLocalizerFactory>();
        _localizer = factory.Create("Resources", "ETS2LA.Translations");
    }

    /// <summary>
    ///  Translates a string.
    ///  `_("My String {0}", var);`
    /// </summary>
    public static string _(string name, params object[] arguments)
    {
        if (_localizer == null) return string.Format(name, arguments);
        return _localizer[name, arguments];
    }


    /// <summary>
    ///  Translates a string with pluralization.
    ///  ```
    ///  _n("Singular {0} value", "Plural {0} values", count, var);
    ///  ```
    /// </summary>
    public static string _n(string singular, string plural, int count, params object[] arguments)
    {
        if (_localizer == null) 
            return string.Format(count == 1 ? singular : plural, arguments);

        // OrchardCore handles plural indexing automatically
        return _localizer[singular, arguments]; 
    }
}