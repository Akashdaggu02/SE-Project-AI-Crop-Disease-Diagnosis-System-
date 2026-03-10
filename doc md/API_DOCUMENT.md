# AI Crop Diagnosis System - API Documentation

This document describes the REST API endpoints available in the AI Crop Diagnosis Backend System. The backend is implemented using Python and Flask and follows RESTful API design principles.

## Base URL
- **Local Development**: `http://localhost:5000`
- **Backend Deployment URL**: `https://ai-crop-diagnosis-backend.onrender.com` (Example)
- **ML Service Deployment URL**: `https://ai-crop-diagnosis-ml.onrender.com` (Example)

## Authentication
Most endpoints (except registration and login) require authentication using a JSON Web Token (JWT). The token must be sent in the request header in the following format:
`Authorization: Bearer <token>`

---

## 1. Authentication & User Management
**Base Path**: `/api/user`

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| POST | `/register` | Register a new farmer account | Public |
| POST | `/login` | Login and receive an access token | Public |
| GET | `/profile` | Retrieve details of the current user | Protected |
| PUT | `/profile` | Update user profile information | Protected |
| PUT | `/language` | Update preferred language for diagnosis | Protected |
| POST | `/send-otp` | Send email verification OTP | Public |
| POST | `/verify-email-otp` | Verify email OTP after registration | Public |
| POST | `/forgot-password` | Send password-reset OTP | Public |
| POST | `/reset-password` | Set a new password using OTP | Public |

---

## 2. Crop Diagnosis & History
**Base Path**: `/api/diagnosis`

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| POST | `/detect` | Detect disease from an uploaded image | Public/Protected |
| GET | `/history` | Retrieve past diagnosis history | Protected |
| GET | `/:id` | Get full details of a specific diagnosis | Protected |
| GET | `/voice/:filename` | Retrieve AI voice diagnosis audio | Public |

---

## 3. Cost Analysis & Reports
**Base Path**: `/api/cost`

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| POST | `/calculate` | Calculate treatment/prevention costs | Protected |
| GET | `/report/:id` | Generate a downloadable cost report | Protected |

---

## 4. AI Chatbot & Support
**Base Path**: `/api/chatbot`

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| POST | `/message` | Send a query to the agricultural assistant | Public/Protected |
| POST | `/upload` | Upload media (image/audio) for chat | Public |

---

## 5. Weather & Translations
**Base Path**: `/api/weather` & `/api/translations`

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| GET | `/api/weather` | Get weather data for coordinates | Public |
| GET | `/api/translations` | Retrieve all UI text translations | Public |
| POST | `/api/translations/batch` | Translate multiple text strings | Public |

---

## Middleware / Security Logic

### `verify_token`
This logic protects private routes by verifying the JWT token sent in the `Authorization` header. If the token is valid, the system retrieves the `user_id` and serves data belonging only to that user.

### Language Detection
Endpoints like `/detect` and `/message` automatically detect the user's preferred language from their profile or the request form to provide localized output in English, Hindi, Telugu, Tamil, Kannada, or Marathi.
