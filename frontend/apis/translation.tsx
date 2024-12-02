declare var require: {
    context(
        directory: string,
        useSubdirectories: boolean,
        regExp: RegExp
    ): {
        keys(): string[];
        <T>(id: string): T;
        resolve(id: string): string;
    };
};

interface Translation {
    [key: string]: string;
}

export const translations: { [key: string]: Translation } = {};
export var currentLanguage: string = "en";

export const loadTranslations = async () => {
    const context = require.context('@/translations', false, /\.json$/);
    const translationFiles: { [key: string]: Translation } = {};
  
    context.keys().forEach((key: string) => {
        const language = key.replace('./', '').replace('.json', '');
        translationFiles[language] = context(key);
    });

    Object.assign(translations, translationFiles);
};

export const translate = (key: string, ...values: any[]): string => {
    const translation = translations[currentLanguage]?.[key];
    if (!translation) {
        return key;
    }

    return translation.replace(/{(\d+)}/g, (match, number) => {
        return values[number] !== undefined ? values[number] : match;
    });
}

export const changeLanguage = async (language: string) => {
    currentLanguage = language;
};