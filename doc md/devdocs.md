# Developer Documentation (DevDocs)

## 1. Project Overview

The **AI Crop Diagnosis System** is a comprehensive solution designed to help farmers detect crop diseases using deep learning. It consists of a mobile application for end-users and a backend server that handles image processing, disease prediction, and data management.

**Key Features:**
*   **Disease Detection:** Uses TensorFlow/Keras models to identify diseases in crops: **Grape, Maize, Potato, Rice, Tomato, and Cotton**.
*   **Multilingual Support:** English, Hindi, Telugu, Tamil, Kannada, Marathi.
*   **Treatment Recommendations:** Provides chemical and organic treatment options based on disease severity.
*   **Chatbot:** AI-powered assistant (Google Gemini) for farming queries and diagnosis explanation.
*   **Offline First:** Critical features work without internet.

---

## 2. Setup Guide

### Prerequisites
*   **Python 3.8+**
*   **Node.js 18+** & **npm**
*   **Expo Go** app on your mobile device (Android/iOS)

### Backend Setup
1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Configuration:**
    Create a `.env` file in `backend/` with the following:
    ```env
    GOOGLE_GEMINI_API_KEY=your_gemini_key
    WEATHER_API_KEY=your_openweather_key
    MONGODB_URI=mongodb+srv://your_username:password@cluster.mongodb.net/
    MONGODB_DB_NAME=agri_ai
    SECRET_KEY=dev_secret_key
    PORT=5000
    DEBUG=True
    ```
5.  **Initialize Database:**
    ```bash
    cd ../database/seed
    # Use the MongoDB seeding script
    python seed_database_mongo.py
    cd ../../backend
    ```
6.  **Run the Server:**
    ```bash
    python app.py
    # Server runs on http://localhost:5000
    ```

### Frontend Setup
1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend-mobile
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Start the generic Metro bundler:**
    ```bash
    npx expo start
    ```
4.  **Run on Device:**
    *   Scan the QR code with **Expo Go**.
    *   Ensure your phone and computer are on the **same Wi-Fi network**.

---

## 3. Architecture / Design

### System Architecture
The system follows a typical Client-Server architecture.

```mermaid
graph TD
    Client["Mobile App (React Native/Expo)"]
    Server["Backend API (Flask)"]
    DB[("MongoDB Atlas")]
    AI["AI Models (TensorFlow)"]
    Ext["External APIs"]

    Client -- HTTP/JSON --> Server
    Server -- Queries --> DB
    Server -- Inference --> AI
    Server -- Requests --> Ext
    Ext --> |"Gemini/Weather"| Server
```

### Modules
*   **Frontend (`frontend-mobile`):**
    *   `app/`: Screens and routing (Expo Router).
    *   `components/`: Reusable UI components.
    *   `services/`: API integration (`api.ts`).
    *   `context/`: State management (Auth, Language).
*   **Backend (`backend`):**
    *   `app.py`: Entry point.
    *   `api/routes/`: Blueprints for `user`, `diagnosis`, `chatbot`, `cost`, `weather`.
    *   `database/`: Database connection and schema interactions.
    *   `ml/`: Model loading and prediction logic.
*   **Database (`database`):**
    *   MongoDB Atlas Cloud Hosting.
    *   Seeding scripts (`seed/seed_database_mongo.py`).

---

## 4. API Documentation

Base URL: `http://localhost:5000/api`

### User Endpoints
*   **Register:** `POST /user/register`
*   **Login:** `POST /user/login`
    *   Returns: `{ "token": "jwt_token", "user_id": 1 }`
*   **Profile:** `GET /user/profile`, `PUT /user/profile`
*   **Language:** `PUT /user/language`

### Diagnosis Endpoints
*   **Detect Disease:** `POST /diagnosis/detect`
    *   Body: `image` (file), `crop` (string)
    *   Response: JSON with disease name, confidence, and treatment.
*   **History:** `GET /diagnosis/history`
*   **Details:** `GET /diagnosis/<id>`

### Cost Endpoints
*   **Calculate:** `POST /cost/calculate`
    *   Body: `{ "diagnosis_id": 1, "land_area": 5 }`

### Chatbot Endpoints
*   **Message:** `POST /chatbot/message`
    *   Body: `{ "message": "How to treat blight?" }`

---

## 5. Database Collections

The system uses **MongoDB**.

### Key Collections
*   **Users (`users`)**
    *   `email`, `password_hash`, `name`, `farm_size`, `preferred_language`.
*   **Diseases (`diseases`)**
    *   `crop`, `disease_name`, `description`, `symptoms`, `prevention_steps`.
*   **History (`diagnosis_history`)**
    *   `user_id`, `crop`, `disease`, `image_path`, `confidence_score`, `timestamp`.
*   **Pesticides (`pesticides`)**
    *   `name`, `type`, `target_diseases`, `dosage`, `cost_per_unit`.
*   **Chat Logs (`chatbot_conversations`)**
    *   `user_id`, `message`, `response`, `timestamp`.

---

## 6. Coding Standards

### Python (Backend)
*   **Style:** Follow **PEP 8** guidelines.
*   **Naming:** `snake_case` for functions/variables, `PascalCase` for classes.
*   **Linting:** Use `pylint` or `flake8` to check for issues.
*   **Structure:** Keep routes, services, and models separated.

### TypeScript/React Native (Frontend)
*   **Style:** Follow standard React formatting (Prettier recommended).
*   **Naming:** `PascalCase` for components (`MyComponent.tsx`), `camelCase` for functions/variables.
*   **Typing:** Use strict **TypeScript** types/interfaces. Avoid `any` whenever possible.
*   **Component Structure:**
    *   Props interface defined at the top.
    *   Functional components with hooks.

---

---

## 7. Deployment Status

### Backend (Flask)
*   **Platform:** Render
*   **CI/CD:** GitHub Actions (Backend CI)
*   **Status:** ✅ Deployed and operational.

### Web Frontend (Expo Web)
*   **Platform:** Vercel
*   **Project Name:** `agri-ai`
*   **Build Command:** `cd frontend-mobile && npm install && npx expo export -p web`
*   **Output Directory:** `frontend-mobile/dist`
*   **Status:** ✅ Deployed and live.

### Mobile App (Android/iOS)
*   **Platform:** EAS (Expo Application Services)
*   **Build Tool:** `eas-cli`
*   **Android Package:** `com.mohansai1810.smartcrophealth`
*   **Status:** ✅ Build successful (APK/AAB generated).

---

## 8. Build & Deployment Commands

### Building for Web
```bash
# From the project root
# The build is automatically handled by Vercel using vercel.json configuration
```

### Building for Mobile (EAS)
```bash
# Navigate to frontend
cd frontend-mobile

# Trigger Android APK build
eas build --platform android --profile preview

# Trigger Production build
eas build --platform android --profile production
```

## 9. Troubleshooting

### Common Issues
*   **"Network Request Failed" on Mobile:**
    *   **Fix:** Ensure the phone is on the **same Wi-Fi** as the backend. Update the `API_URL` in `frontend-mobile/services/api.ts` to your computer's local IP (e.g., `http://192.168.1.10:5000`). localhost won't work on a physical device.

*   **Database Errors / Connection:**
    *   **Fix:** Ensure your MongoDB URI is correct in the `.env` file and that your IP address is whitelisted in MongoDB Atlas.

*   **"Module not found" in Frontend:**
    *   **Fix:** Run `npm install` to ensure all dependencies are present. Try `npx expo start -c` to clear the cache.

*   **Model Loading Errors:**
    *   **Fix:** Ensure `.h5` model files exist in `backend/models/`. Confirm TensorFlow versions match requirements.
