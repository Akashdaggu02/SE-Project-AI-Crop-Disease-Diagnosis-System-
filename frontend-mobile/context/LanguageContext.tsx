import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { Translations, LanguageCode } from '../constants/Translations';
import { useAuth } from './AuthContext';

interface LanguageContextType {
    language: LanguageCode;
    setLanguage: (lang: LanguageCode) => void;
    t: (key: keyof typeof Translations['en']) => string;
    translations: typeof Translations['en'];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { user } = useAuth();
    const [language, setLanguageState] = useState<LanguageCode>('en');

    // Sync with user preference if logged in
    useEffect(() => {
        if (user?.preferred_language && Object.keys(Translations).includes(user.preferred_language)) {
            console.log('Syncing language from user pref:', user.preferred_language);
            setLanguageState(user.preferred_language as LanguageCode);
        }
    }, [user?.preferred_language]);

    const setLanguage = (lang: LanguageCode) => {
        console.log('Setting language to:', lang);
        setLanguageState(lang);
    };

    const t = (key: keyof typeof Translations['en']) => {
        const translation = Translations[language]?.[key];
        if (!translation) console.log(`Missing translation for ${key} in ${language}`);
        return translation || Translations['en'][key] || key;
    };

    const value = {
        language,
        setLanguage,
        t,
        translations: Translations[language],
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
