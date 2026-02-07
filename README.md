# 🌾 AI Crop Diagnosis System

A comprehensive, farmer-friendly mobile and web application for crop disease detection, diagnosis, and treatment recommendations with multilingual support.

## ✨ Features

### 🔍 Disease Detection & Diagnosis
- **Real-time Detection**: Upload or capture crop images for instant analysis.
- **High Accuracy**: Powered by deep learning models (TensorFlow/Keras).
- **Supported Crops**: **Grape, Maize, Potato, Rice, Tomato**.
- **Detailed Diagnosis**: Identifies specific diseases (e.g., Late Blight, Bacterial Spot) or confirms health.
- **Severity Estimation**: Detects the severity level of the infection.

### 💊 Treatment & Prevention
- **Pesticide Recommendations**: Suggests effective pesticides with dosage and application instructions.
- **Organic Alternatives**: Provides eco-friendly / organic treatment options.
- **Prevention Tips**: actionable advice to prevent future outbreaks.
- **Cost Calculation**: Estimates treatment costs based on land area.

### 🌐 Multilingual Support
- **Languages**: English, Hindi (हिंदी), Telugu (తెలుగు), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Marathi (मराठी).
- **Voice Support**: Text-to-speech for diagnosis results and advice.
- **Dynamic Translation**: UI and content translated on-the-fly.

### 📱 User Experience
- **Mobile App**: Built with React Native & Expo for iOS and Android.
- **Offline Capable**: Essential features work with cached data.
- **Chatbot Assistant**: AI-powered (Gemini) chatbot to answer farming queries.
- **History**: Track past diagnoses and treatments.

## 🏗️ Technology Stack

### Frontend (Mobile App)
- **Framework**: [Expo](https://expo.dev/) (React Native)
- **Language**: TypeScript
- **Networking**: Axios
- **UI Components**: React Native Elements, Vector Icons

### Backend (API)
- **Framework**: Flask (Python)
- **Database**: SQLite
- **ML Engine**: TensorFlow / Keras
- **Image Processing**: OpenCV
- **AI Services**: Google Gemini (Chatbot), Google Translate, gTTS (Voice)

## 📁 Project Structure

```
AI-Crop-Diagnosis/
├── backend/                # Flask API & ML Logic
│   ├── app.py              # Main Application Entry
│   ├── api/                # API Routes (User, Diagnosis, Cost, etc.)
│   ├── config/             # Settings & Environment Variables
│   ├── ml/                 # Model Loading & Prediction Logic
│   └── start_server.bat    # Script to launch backend
├── database/               # SQLite Database & Seeds
│   ├── seed/               # Initial Data (Pesticides, Diseases)
│   └── crop_diagnosis.db   # (Auto-generated) Database File
├── frontend-mobile/        # React Native Mobile App
│   ├── app/                # Expo Router Pages
│   ├── components/         # Reusable UI Components
│   └── constants/          # App Constants & Styles
├── models/                 # Pre-trained .h5 Models
│   ├── grape_disease_model.h5
│   ├── maize_disease_model.h5
│   ├── potato_disease_model.h5
│   ├── rice_disease_model.h5
│   └── tomato_disease_model.h5
├── training/               # Scripts used to train the models
└── uploads/                # (Auto-generated) User Uploaded Images
```

## 🚀 Setup Instructions

### Prerequisites
- **Node.js**: v18+ (for frontend)
- **Python**: v3.8+ (for backend)
- **Expo Go App**: To run on your phone.

### 1. Backend Setup

Navigate to the `backend` directory and install dependencies:

```bash
cd backend

# Create virtual environment (Optional but Recommended)
python -m venv venv
# Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

# Install Python packages
pip install -r requirements.txt
```

**Configuration**:
- Copy `.env.example` to `.env` (if available) or create a `.env` file in `backend/`.
- Add API keys (Optional for core image/diagnosis features, required for Chatbot/Weather):
  ```env
  GOOGLE_GEMINI_API_KEY=your_key
  WEATHER_API_KEY=your_key
  SECRET_KEY=dev_secret
  ```

**Initialize Database**:
```bash
cd ../database/seed
python seed_database.py
cd ../../backend
```

**Run Server**:
```bash
python app.py
# Server starts at http://localhost:5000
```

### 2. Frontend Setup

Open a new terminal and navigate to `frontend-mobile`:

```bash
cd frontend-mobile

# Install Node dependencies
npm install

# Start the App
npx expo start
```

- Scan the QR code with the **Expo Go** app on your Android/iOS device.
- Or press `a` to run on Android Emulator, `w` for Web.

## 🌍 Supported Crops & Diseases

| Crop | Detectable Conditions |
|------|----------------------|
| **Grape** | Black Rot, ESCA, Leaf Blight, Healthy |
| **Maize** | Blight, Common Rust, Gray Leaf Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Rice** | Bacterial Leaf Blight, Brown Spot, Leaf Smut, Healthy |
| **Tomato** | Bacterial Spot, Early/Late Blight, Leaf Mold, Septoria, Spider Mites, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus, Healthy |

## 📱 API Endpoints

Base URL: `http://localhost:5000/api`

### Auth & User
- `POST /user/register`: Create account
- `POST /user/login`: Get JWT token
- `GET /user/profile`: Get user details
- `PUT /user/language`: Update language preference

### Diagnosis
- `POST /diagnosis/detect`: Upload image & crop type (`grape`, `maize`, `potato`, `rice`, `tomato`)
- `GET /diagnosis/history`: User's diagnosis history
- `GET /diagnosis/<id>`: Specific diagnosis details

### Features
- `POST /cost/calculate`: Estimate treatment costs
- `POST /chatbot/message`: Chat with Agri-Bot
- `GET /weather`: Get local weather advice

## 🐛 Troubleshooting

- **Server won't start?** Check if port 5000 is free or change `PORT` in `.env`.
- **"Network Error" on App?** Ensure your phone and computer are on the **same Wi-Fi**. Update the `API_URL` in `frontend-mobile/services/api.ts` to your computer's local IP (e.g., `http://192.168.1.5:5000`).
- **Database errors?** Delete `database/crop_diagnosis.db` and re-run `python seed_database.py`.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


