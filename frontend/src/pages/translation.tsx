import { GetSettingByKey } from "./settingsServer";

interface Translation {
    [key: string]: string;
}

export const translations: { [key: string]: Translation } = {};
export var currentLanguage: string = "en";

const loadTranslations = async () => {
    const context = require.context('@/translations', false, /\.json$/);
    const translationFiles: { [key: string]: Translation } = {};
  
    context.keys().forEach((key: string) => {
      const language = key.replace('./', '').replace('.json', '');
      translationFiles[language] = context(key) as Translation;
    });

    Object.assign(translations, translationFiles);

};

loadTranslations();

// Take the key and a list of values (to replace {0}, {1}, etc. in the translation)
export const translate = (key: string, ...values: any[]): string => {
    const translation = translations[currentLanguage][key];
    if (!translation) {
        return key;
    }

    return translation.replace(/{(\d+)}/g, (match, number) => {
        return values[number] !== undefined ? values[number] : match;
    });
}