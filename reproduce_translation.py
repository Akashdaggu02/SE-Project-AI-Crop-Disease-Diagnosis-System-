import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.services.language_service import translate_text, get_all_translations, translate_batch

def test_translation():
    print("--- Single Text Translation ---")
    text = "Hello, how are you?"
    target_lang = "hi" # Hindi
    
    print(f"Testing translation of '{text}' to '{target_lang}'...")
    try:
        translated = translate_text(text, target_lang)
        print(f"Result: {translated}")
        
        if translated == text:
            print("FAILURE: Text was not translated (returned original).")
        else:
            print("SUCCESS: Text was translated.")
            
    except Exception as e:
        print(f"ERROR: Translation raised exception: {e}")

    print("\n--- Batch Translation (Simulating Frontend) ---")
    # Simulate the large dictionary from Translations.ts
    mock_translations = {
        "preferences": "Preferences",
        "appLanguage": "App Language",
        "pushNotifications": "Push Notifications",
        "supportLegal": "Support & Legal",
        "helpCenter": "Help Center",
        "privacyPolicy": "Privacy Policy",
        "appVersion": "App Version",
        "logOut": "Log Out",
        "guestUser": "Guest User",
        "browseMode": "Browse Mode",
        "registerFullAccess": "Register for Full Access",
        "madeWithLove": "Made with ❤️ for Indian Farmers",
        "signOutTitle": "Sign Out",
        "signOutMessage": "Are you sure you want to log out?",
        "cancel": "Cancel",
        "success": "Success",
        "languageChanged": "Language changed to",
        "error": "Error",
        "failedUpdate": "Failed to update language preference",
        "namaste": "Namaste,",
        "farmer": "Farmer!",
        "selectLanguage": "Select Language",
        "weather": "Weather",
        "humidity": "Humidity",
        "wind": "Wind",
        "pressure": "Pressure",
        "scanCrop": "Scan Crop",
        "uploadImage": "Upload Image",
        "recentDiagnoses": "Recent Diagnoses",
        "viewAll": "View All",
        "noDiagnoses": "No diagnoses found",
        "startDiagnosis": "Start a diagnosis scan or upload",
        "whatWouldYouLikeToDo": "What would you like to do?",
        "instantDiagnosis": "Instant disease diagnosis",
        "supportedCrops": "Supported Crops",
        "enableGps": "Enable GPS",
        "gpsEnabled": "GPS Enabled",
        "crop_tomato": "Tomato",
        "crop_cotton": "Cotton",
        "crop_wheat": "Wheat",
        "crop_rice": "Rice",
        "crop_potato": "Potato",
        "crop_corn": "Corn",
        "crop_grape": "Grape",
        "analyzeDisease": "Analyze Disease",
        "tipsTitle": "📸 Tips for Best Results:",
        "tip1": "• Ensure good lighting (natural light works best)",
        "tip2": "• Focus clearly on the affected leaf",
        "tip3": "• Avoid shadows and blurry images",
        "tip4": "• Fill the frame with the leaf",
        "tab_diagnose": "Diagnose",
        "tab_history": "History",
        "tab_chatbot": "Chatbot",
        "tab_explore": "Explore",
        "saveYourHistory": "Save Your History",
        "trackHealth": "Create a free account to track your farm's health over time.",
        "registerNow": "Register Now",
        "guestHistorySubtitle": "Sign in to keep track of your crop diagnoses, treatments, and progression over time.",
        "loginRegister": "Login / Register",
        "weatherUnavailable": "Weather Unavailable",
        "notAvailable": "N/A",
        "chatbotWelcome": "Hello! I'm your AI Agricultural Assistant. How can I help you with your crops today?",
        "extra_1": "Extra item 1", "extra_2": "Extra item 2", "extra_3": "Extra item 3", "extra_4": "Extra item 4", "extra_5": "Extra item 5",
        "extra_6": "Extra item 6", "extra_7": "Extra item 7", "extra_8": "Extra item 8", "extra_9": "Extra item 9", "extra_10": "Extra item 10",
        "extra_11": "Extra item 11", "extra_12": "Extra item 12", "extra_13": "Extra item 13", "extra_14": "Extra item 14", "extra_15": "Extra item 15",
        "extra_16": "Extra item 16", "extra_17": "Extra item 17", "extra_18": "Extra item 18", "extra_19": "Extra item 19", "extra_20": "Extra item 20",
        "extra_21": "Extra item 21", "extra_22": "Extra item 22", "extra_23": "Extra item 23", "extra_24": "Extra item 24", "extra_25": "Extra item 25",
        "extra_26": "Extra item 26", "extra_27": "Extra item 27", "extra_28": "Extra item 28", "extra_29": "Extra item 29", "extra_30": "Extra item 30",
        "extra_31": "Extra item 31", "extra_32": "Extra item 32", "extra_33": "Extra item 33", "extra_34": "Extra item 34", "extra_35": "Extra item 35",
        "extra_36": "Extra item 36", "extra_37": "Extra item 37", "extra_38": "Extra item 38", "extra_39": "Extra item 39", "extra_40": "Extra item 40",
        "extra_41": "Extra item 41", "extra_42": "Extra item 42", "extra_43": "Extra item 43", "extra_44": "Extra item 44", "extra_45": "Extra item 45",
        "extra_46": "Extra item 46", "extra_47": "Extra item 47", "extra_48": "Extra item 48", "extra_49": "Extra item 49", "extra_50": "Extra item 50",
        "extra_51": "Extra item 51", "extra_52": "Extra item 52", "extra_53": "Extra item 53", "extra_54": "Extra item 54", "extra_55": "Extra item 55",
        "extra_56": "Extra item 56", "extra_57": "Extra item 57", "extra_58": "Extra item 58", "extra_59": "Extra item 59", "extra_60": "Extra item 60",
        "extra_61": "Extra item 61", "extra_62": "Extra item 62", "extra_63": "Extra item 63", "extra_64": "Extra item 64", "extra_65": "Extra item 65",
        "extra_66": "Extra item 66", "extra_67": "Extra item 67", "extra_68": "Extra item 68", "extra_69": "Extra item 69", "extra_70": "Extra item 70",
    }
    
    print(f"Translating batch of {len(mock_translations)} items to 'hi'...")
    try:
        translated_batch = translate_batch(mock_translations, target_lang)
        print("Batch translation completed.")
        
        # Verify a key
        key = "chatbotWelcome"
        original = mock_translations[key]
        translated = translated_batch.get(key)
        
        print(f"Key '{key}':")
        print(f"  Original: {original}")
        print(f"  Translated: {translated}")
        
        if translated == original:
            print("FAILURE: Batch item was not translated.")
        else:
            print("SUCCESS: Batch item translated.")

        # Check total count
        print(f"Total input: {len(mock_translations)}")
        print(f"Total output: {len(translated_batch)}")

    except Exception as e:
        print(f"ERROR: Batch translation failed: {e}")

if __name__ == "__main__":
    test_translation()
