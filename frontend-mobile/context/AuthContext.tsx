import React, { createContext, useState, useEffect, useContext } from 'react';
import { saveItem, getItem, deleteItem } from '../services/storage';
import api from '../services/api';

interface User {
    id: number;
    email: string;
    name: string;
    preferred_language: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    isGuest: boolean;
    signIn: (token: string, userData: User) => Promise<void>;
    signOut: () => Promise<void>;
    continueAsGuest: () => void;
    updateUser: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isGuest, setIsGuest] = useState(false);

    useEffect(() => {
        loadStorageData();
    }, []);

    const loadStorageData = async () => {
        try {
            const storedToken = await getItem('userToken');
            const storedUser = await getItem('userData');
            if (storedToken && storedUser) {
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
                setIsGuest(false);
            } else {
                // Default to guest if no credentials found
                setIsGuest(true);
            }
        } catch (e) {
            console.error('Failed to load auth data', e);
            setIsGuest(true);
        } finally {
            setIsLoading(false);
        }
    };

    const signIn = async (token: string, userData: User) => {
        await saveItem('userToken', token);
        await saveItem('userData', JSON.stringify(userData));
        await deleteItem('isGuest');
        setToken(token);
        setUser(userData);
        setIsGuest(false);
    };

    const signOut = async () => {
        await deleteItem('userToken');
        await deleteItem('userData');
        await deleteItem('isGuest');
        setToken(null);
        setUser(null);
        setIsGuest(false);
    };

    const continueAsGuest = async () => {
        await saveItem('isGuest', 'true');
        await deleteItem('userToken');
        await deleteItem('userData');
        setIsGuest(true);
        setToken(null);
        setUser(null);
    };

    const updateUser = async (userData: Partial<User>) => {
        if (user) {
            const updatedUser = { ...user, ...userData };
            await saveItem('userData', JSON.stringify(updatedUser));
            setUser(updatedUser);
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, isLoading, isGuest, signIn, signOut, continueAsGuest, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
