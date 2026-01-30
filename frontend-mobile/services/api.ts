import axios from 'axios';
import { getItem } from './storage';
import { Platform } from 'react-native';

// Replace with your local IP if testing on a physical device
const API_URL = Platform.OS === 'android' ? 'http://10.0.2.2:5000/api' : 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_URL,
    // Don't set default Content-Type - let axios handle it based on request data
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    async (config) => {
        const token = await getItem('userToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
