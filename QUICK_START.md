# 🚀 Quick Start Guide

## Step-by-Step Instructions to Run the Server

### 1️⃣ Install Dependencies (Currently Running...)
```bash
cd backend
pip install -r requirements.txt
```
⏳ This may take 5-10 minutes due to TensorFlow and other large packages.

### 2️⃣ Initialize Database
```bash
cd ../database/seed
python seed_database_mongo.py
```
✅ This will connect to MongoDB Atlas and populate it with diseases and pesticides.

### 3️⃣ Start the Server
```bash
cd ../../backend
python app.py
```
🌐 Server will start at: http://localhost:5000

### 4️⃣ Test the Server
Open a new terminal and run:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Crop Diagnosis API",
  "version": "1.0.0"
}
```

## 🧪 Quick Test with Your Sample Image

### Register a User
```bash
curl -X POST http://localhost:5000/api/user/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"farmer@test.com\",\"password\":\"test123\",\"name\":\"Test Farmer\"}"
```

### Login
```bash
curl -X POST http://localhost:5000/api/user/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"farmer@test.com\",\"password\":\"test123\"}"
```

Copy the `token` from the response!

### Detect Disease
```bash
curl -X POST http://localhost:5000/api/diagnosis/detect ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -F "image=@../sample.JPG" ^
  -F "crop=tomato"
```

## 📝 Notes

- **Database**: MongoDB Atlas Connection (Manage in `.env`)
- **Uploads**: Saved in `backend/uploads/` (auto-created)
- **Voice Files**: Saved in `backend/voice_outputs/` (auto-created)
- **Port**: Default is 5000, change in `.env` if needed

## ⚠️ Troubleshooting

### If installation fails:
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then retry
pip install -r requirements.txt
```

### If port 5000 is in use:
Edit `backend/.env` and change:
```
PORT=5001
```

### If database errors occur:
```bash
# Check MongoDB URI in backend/.env
# Re-run seeding script
cd database\seed
python seed_database_mongo.py
```

## ✅ Success Indicators

When everything is working:
- ✅ No errors during `pip install`
- ✅ Database seeded successfully (23 diseases, 15 pesticides)
- ✅ Server starts with "Running on http://0.0.0.0:5000"
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Disease detection returns results

## 🎯 What's Next?

Once the server is running:
1. Test all API endpoints (see `API_TESTING_GUIDE.md`)
2. Build the mobile frontend (React Native/Expo)
3. Connect mobile app to this backend
4. Deploy to production server

## 📚 Documentation

- `README.md` - Complete documentation
- `API_TESTING_GUIDE.md` - How to test APIs
- `walkthrough.md` - Feature overview
