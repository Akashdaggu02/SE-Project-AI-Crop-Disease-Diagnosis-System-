import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, KeyboardAvoidingView, Platform, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Mail, Lock, User, Leaf } from 'lucide-react-native';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { T } from '../components/ui/T';

export default function LoginScreen() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { signIn, continueAsGuest } = useAuth();
    const router = useRouter();
    const { t } = useLanguage();

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert(t('error'), t('loginErrorMissing'));
            return;
        }

        setLoading(true);
        try {
            // Ask the server to check the credentials
            const response = await api.post('/user/login', { email, password });

            // If correct, save the user info and token (the VIP pass)
            await signIn(response.data.token, response.data.user);

            // Go to the main dashboard
            router.replace('/(tabs)');
        } catch (error: any) {
            const message = error.response?.data?.error || t('loginErrorInvalid');
            Alert.alert(t('loginErrorTitle'), message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                <View style={styles.header}>
                    <View style={styles.logoContainer}>
                        <Leaf color="#4caf50" size={48} />
                    </View>
                    <T style={styles.title}>appTitle</T>
                    <T style={styles.subtitle}>appSubtitle</T>
                </View>

                <View style={styles.form}>
                    <View style={styles.inputContainer}>
                        <Mail size={20} color="#666" style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder={t('emailPlaceholder')}
                            value={email}
                            onChangeText={setEmail}
                            keyboardType="email-address"
                            autoCapitalize="none"
                        />
                    </View>

                    <View style={styles.inputContainer}>
                        <Lock size={20} color="#666" style={styles.inputIcon} />
                        <TextInput
                            style={styles.input}
                            placeholder={t('passwordPlaceholder')}
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry
                        />
                    </View>

                    <TouchableOpacity
                        style={styles.loginButton}
                        onPress={handleLogin}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <T style={styles.loginButtonText}>loginButton</T>
                        )}
                    </TouchableOpacity>

                    {/* Guest Access Button: For users who just want to try it out first */}
                    <TouchableOpacity
                        style={styles.guestButton}
                        onPress={() => {
                            continueAsGuest();
                            router.replace('/(tabs)');
                        }}
                    >
                        <T style={styles.guestButtonText}>continueGuest</T>
                    </TouchableOpacity>

                    <View style={styles.footer}>
                        <T style={styles.footerText}>noAccount</T>
                        <TouchableOpacity onPress={() => router.push('/register')}>
                            <T style={styles.footerLink}>registerNow</T>
                        </TouchableOpacity>
                    </View>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8fdf8',
    },
    scrollContainer: {
        flexGrow: 1,
        justifyContent: 'center',
        padding: 24,
    },
    header: {
        alignItems: 'center',
        marginBottom: 40,
    },
    logoContainer: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#e8f5e9',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#2e7d32',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
    },
    form: {
        width: '100%',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: '#e0e0e0',
        marginBottom: 16,
        paddingHorizontal: 12,
        height: 56,
    },
    inputIcon: {
        marginRight: 12,
    },
    input: {
        flex: 1,
        fontSize: 16,
        color: '#333',
    },
    loginButton: {
        backgroundColor: '#4caf50',
        borderRadius: 12,
        height: 56,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 8,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
    },
    guestButton: {
        backgroundColor: 'transparent',
        borderRadius: 12,
        height: 56,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 12,
        borderWidth: 1,
        borderColor: '#4caf50',
    },
    guestButtonText: {
        color: '#4caf50',
        fontSize: 16,
        fontWeight: '600',
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 24,
    },
    footerText: {
        fontSize: 14,
        color: '#666',
    },
    footerLink: {
        fontSize: 14,
        color: '#2e7d32',
        fontWeight: 'bold',
    },
});
