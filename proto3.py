import base64
import json
import time
import requests
import serial
from typing import Dict, Any
#import datetime
import random

interval=19

# Record start time for performance tracking
start_time = time.perf_counter()

ESP_IP = "http://192.168.0.200"   # your ESP32-CAM local IP
CAPTURE_URL = f"{ESP_IP}/capture"

# --- Hardware Setup ---
ARDUINO_PORT = "COM10"
BAUD_RATE = 9600
try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino reset
    print(f"✅ Hardware Online: {ARDUINO_PORT}")
except Exception as e:
    ser = None
    print(f"⚠️ Simulation Mode: Hardware not found on {ARDUINO_PORT}")

# --- AI Configuration ---
API_KEY = "UR_API_KEY_FROM_GGLaiSTUDIO"
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def trigger_hardware(action_type: str):
    """Triggers Arduino components based on danger level."""
    if not ser:
        print(f"[SIMULATION] {action_type.upper()} would have triggered.")
        return

    if action_type == "pulse":
        # HIGH THREAT: Pulse + Buzzer
        print(">>> 🚨 ACTION: FIRE PULSE + BUZZER (High Threat)")
        ser.write(b't') # Trigger Pulse
        ser.flush()
        time.sleep(0.2) 
        ser.write(b'b') # Trigger Buzzer
        ser.flush()
    elif action_type == "buzz":
        # LOW THREAT: Buzzer Only
        print(">>> ⚠️ ACTION: BUZZER ONLY (Warning)")
        ser.write(b'b')
        ser.flush()

def write_json_log(data: Dict[str, Any], image_name: str):
    """Saves AI response to a local JSON file for record-keeping."""
    safe_name = image_name.replace(".", "_")
    file_path = f"JSON_{safe_name}.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"💾 Results logged to: {file_path}")

def get_frame_base64():
    r = requests.get(CAPTURE_URL, timeout=5)
    if r.status_code == 200:
        # JPEG bytes → base64
        b64 = base64.b64encode(r.content).decode("utf-8")
        return b64
    else:
        raise Exception("Failed to capture image")

def analyze_image():
    """Encodes image, queries Gemini AI, and handles hardware triggers."""
    print(f"\n" + "="*50)
    print(f"🔍 ANALYZING: ESP32 CAM FEED")
    print("="*50)

    try:
        img_b64 = get_frame_base64()
    except:
        print(f"❌ Error: Image could not be received.")
        return

    # Step 2: Prepare AI Prompt & Schema
    system_prompt = (
        "You are an autonomous security AI. Analyze for theft. "
        "Classify 'danger_level' as 'low' (shoplifting/concealment) "
        "or 'high' (armed robbery, violence, or multiple masked intruders). "
        "Respond ONLY in valid JSON."
    )

    user_query = "Analyze for theft. Return JSON: is_theft (bool), confidence (0-1), danger_level (low/high), and reasoning."

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": user_query},
                {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
            ]
        }],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"responseMimeType": "application/json"}
    }

    # Step 3: API Request with Exponential Backoff
    retries = 3
    for i in range(retries):
        try:
            print(f"📡 Uploading to Security Cloud...")
            response = requests.post(BASE_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                print(f"⚠️ AI Blocked or Failed. Response: {result}")
                return

            candidate = result['candidates'][0]
            raw_text = candidate['content']['parts'][0]['text']
            data = json.loads(raw_text)
            
            write_json_log(data, str(random.randint(1,100)))

            is_theft = data.get("is_theft", False)
            danger = data.get("danger_level", "low").lower()
            conf = data.get("confidence", 0.0)

            print(f"\nRESULT: {'🔴 THEFT DETECTED' if is_theft else '🟢 AREA SECURE'}")
            print(f"CONFIDENCE: {conf*100:.1f}%")
            print(f"DANGER LEVEL: {danger.upper()}")
            print(f"REASONING: {data.get('reasoning')}\n")

            # --- REFINED HARDWARE TRIGGER LOGIC ---
            if is_theft:
                # Strictly separate Low vs High danger actions
                if danger == "high":
                    trigger_hardware("pulse")
                else:
                    # Low danger theft (shoplifting) only triggers buzz
                    trigger_hardware("buzz")
            else:
                print(">>> SYSTEM: No threat detected. No action taken.")
            
            break 

        except Exception as e:
            if i < retries - 1:
                time.sleep(2 ** i)
                continue
            print(f"❌ System Error: {e}")

if __name__ == "__main__":
    
    while True:
        try:
            analyze_image()
            time.sleep(interval)
        except KeyboardInterrupt:
            break

    if ser:
        ser.close()
        print("\n🔌 Serial connection closed safely.")

    total_time = time.perf_counter() - start_time
    print(f"🏁 Total Process Runtime: {total_time:.3f} seconds")