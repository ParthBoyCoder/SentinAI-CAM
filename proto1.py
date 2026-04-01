import base64
import json
import time
import requests
import serial

# --- Hardware Setup ---
ARDUINO_PORT = "COM10"
BAUD_RATE = 9600
try:
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 
    print(f"Hardware Online: {ARDUINO_PORT}")
except:
    ser = None
    print("Running in Simulation Mode (No Arduino)")

# --- AI Setup ---
API_KEY = "UR_API_KEY_FROM_GGLaiSTUDIO"
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def trigger_hardware(action_type: str):
    if not ser: return
    if action_type == "pulse":
        ser.write(b't')
        ser.write(b'b')
        print(">>> ACTION: FIRE PULSE (High Threat)")
    elif action_type == "buzz":
        ser.write(b'b')
        print(">>> ACTION: BUZZER (Warning)")
    ser.flush()

def analyze_image(image_path: str):
    try:
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: File {image_path} not found.")
        return

    # Define the "Danger Logic" in the prompt
    system_prompt = (
        "You are an autonomous security system. Analyze for theft. "
        "Classify 'danger_level' as 'low' (suspicious behavior) or 'high' (active concealment/aggression). "
        "Respond ONLY in JSON."
    )

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": "Analyze for theft. Return JSON with keys: is_theft (bool), confidence (0-1), danger_level (low/high), and reasoning."},
                {"inlineData": {"mimeType": "image/png", "data": img_data}}
            ]
        }],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        response = requests.post(BASE_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Check if candidates exist (Prevents 'candidates' KeyError)
        if 'candidates' not in result or not result['candidates']:
            if 'promptFeedback' in result:
                print(f"AI Blocked: Safety filters triggered. Reason: {result['promptFeedback']}")
            else:
                print(f"AI Error: No candidates returned. Full response: {result}")
            return

        # Extract content safely
        candidate = result['candidates'][0]
        if 'content' not in candidate:
            print(f"AI Error: Finish reason: {candidate.get('finishReason')}. The AI might have refused the image.")
            return

        raw_text = candidate['content']['parts'][0]['text']
        data = json.loads(raw_text)
        
        # --- SENSITIVE TRIGGER LOGIC ---
        is_theft = data.get("is_theft", False)
        danger = data.get("danger_level", "low")
        conf = data.get("confidence", 0.0)

        if is_theft:
            # If AI says danger is 'high' OR confidence is decent, we PULSE.
            if danger == "high" or conf > 0.65:
                trigger_hardware("pulse")
            else:
                trigger_hardware("buzz")
        
        print(f"\nResult: {'THEFT' if is_theft else 'CLEAR'}")
        print(f"Confidence: {conf*100:.1f}% | Level: {danger.upper()}")
        print(f"Reason: {data.get('reasoning')}")

    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    # Add your test images here
    images = ["test1.jpg", "test2.jpg", "test3.jpg"]
    for img in images:
        analyze_image(img)
        time.sleep(1) # Gap between checks
    if ser: ser.close()