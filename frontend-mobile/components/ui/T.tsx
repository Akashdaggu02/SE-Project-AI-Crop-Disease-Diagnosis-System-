import React from 'react';
import { Text, TextProps } from 'react-native';
import { useLanguage } from '../../context/LanguageContext';

export const T = ({ children, style, ...props }: TextProps & { children: string }) => {
    const { t } = useLanguage();

    // Try to translate the children string.
    // The t function falls back to the key (children) if no translation is found.
    const translatedText = t(children as any);

    return (
        <Text style={style} {...props}>
            {translatedText}
        </Text>
    );
};
