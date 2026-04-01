import base64
import json
import time
import requests
from typing import Dict, Any

start_time = time.perf_counter()

# --- Configuration ---
# The environment provides the API key at runtime.
API_KEY = "UR_API_KEY_FROM_GGLaiSTUDIO"
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def encode_image(image_path: str) -> str:
    """Reads a local image file and returns its base64 encoded string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_for_theft(image_base64: str) -> Dict[str, Any]:
    """
    Sends the image to Gemini 2.5 Flash to determine if theft is occurring.
    Implements exponential backoff and structured JSON output.
    """
    
    # System prompt to define the AI's persona and logic requirements
    system_prompt = (
        "You are a highly advanced security AI specialized in behavioral analysis. "
        "Analyze the provided image for signs of theft, shoplifting, or unauthorized removal of property. "
        "Look for: suspicious concealment, tampering with security tags, or bypassing point-of-sale systems. "
        "Respond ONLY in valid JSON format."
    )

    # The user query requesting the specific analysis
    user_query = (
        "Analyze this image. Determine if a theft is occurring. "
        "Provide a confidence score between 0.0 and 1.0, a boolean 'is_theft', "
        "and a detailed 'reasoning' string explaining your conclusion based on visual cues."
    )

    # Define the expected JSON schema for a structured response
    generation_config = {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "OBJECT",
            "properties": {
                "is_theft": {"type": "BOOLEAN"},
                "confidence": {"type": "NUMBER"},
                "reasoning": {"type": "STRING"}
            },
            "required": ["is_theft", "confidence", "reasoning"]
        }
    }

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": user_query},
                {"inlineData": {"mimeType": "image/png", "data": image_base64}}
            ]
        }],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": generation_config
    }

    # Exponential Backoff Implementation (Rule-compliant)
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(BASE_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            # Extract the text content from the Gemini response structure
            content_text = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content_text)
            
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            if i < retries - 1:
                wait_time = 2 ** i  # 1s, 2s, 4s, 8s, 16s
                time.sleep(wait_time)
                continue
            else:
                return {
                    "error": "Failed to analyze image after multiple attempts.",
                    "details": str(e)
                }

def write_json(data, json_name):
    file_path = f"{json_name}.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data successfully written to {file_path}")

def main(img):
    """
    Main execution flow:
    1. Provide image path.
    2. Encode image.
    3. Run AI analysis.
    4. Display formatted results.
    """
    # Replace 'security_footage.png' with your actual image file path
    image_path = img
    
    print(f"--- Starting Analysis for: {image_path} ---")
    
    try:
        # Step 1: Encode
        img_b64 = encode_image(image_path)
        
        # Step 2: Analyze
        print("Uploading to Security AI (Gemini 2.5 Flash)...")
        analysis = analyze_for_theft(img_b64)

        write_json(analysis, f"JSON_{img}")
        
        # Step 3: Output Results
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
        else:
            status = "🚨 THEFT DETECTED" if analysis['is_theft'] else "✅ NO THEFT DETECTED"
            print("\n" + "="*40)
            print(f"RESULT: {status}")
            print(f"CONFIDENCE: {analysis['confidence'] * 100:.1f}%")
            print(f"REASONING: {analysis['reasoning']}")
            print("="*40)
            
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found. Please ensure the image exists.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main("test_image1.jpg")
    main("test_image2.jpg")

    end_time = time.perf_counter()
    print(f"Total runtime: {end_time - start_time:.3f} seconds")
