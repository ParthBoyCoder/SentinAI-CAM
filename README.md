# SentinAI-Cam: Active AI Surveillance & Deterrent System

SentinAI-Cam is an autonomous, AI-driven security system that bridges the gap between passive recording and active defense. Using an **ESP32-CAM** for live wireless streaming and **Google Gemini 2.5 Flash** for real-time behavioral analysis, the system identifies theft in progress and triggers physical hardware deterrents (Buzzer/Pulse) via an **Arduino** controller.

---

## 🚀 System Architecture

1. **Acquisition (ESP32-CAM):** Captures high-resolution frames and serves them over a local network.
2. **Intelligence (Gemini 2.5 Flash):** Processes frames to identify intent (concealment, aggression, or masked entry).
3. **Execution (Arduino + Relay):** Receives serial commands to trigger a warning buzzer or a high-threat deterrent pulse.

---

## 📂 Project Structure

```text
.
├── proto3.py           # FINAL: Main CCTV Analysis Script (ESP32-CAM Integration)
├── proto2.py           # PROTOTYPE: Batch Processing for local test images
├── proto1.py           # PROTOTYPE: Early logic test with basic AI triggers
├── 1.py                # UTILITY: Manual Hardware Controller (Serial Tester)
├── 2.py                # UTILITY: Image Encoder & JSON Logger tool
├── test1.jpg, test2.jpg... # Test Image Dataset
├── Useless/            # Test Codes I might fill out with junk later
├── JSON_logs/          # Auto-generated AI analysis logs (History)
├── taser1/
│   └── taser1.ino      # Arduino Source Code for Relay/Buzzer control
└── README.md           # You are here!
```

---

## 🛠️ Setup & Installation

### 1. Hardware Setup

- **Arduino:** Connect a Relay to Pin 8 and a Buzzer to Pin 9.
- **ESP32-CAM:** Flash with a standard CameraWebServer or a simple Capture server.
- **Connection:** Connect the Arduino to your PC via USB (Note the COM port, e.g., `COM10`).

### 2. Python Environment Setup

We recommend using a Virtual Environment (`venv`) to keep dependencies isolated.

```bash
# Clone the repository
git clone https://github.com/ParthBoyCoder/SentinAI-CAM
cd SentinAI-CAM

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install necessary libraries
pip install requests pyserial
```

### 3. Configuration

Open `proto3.py` and update the following variables:

- `API_KEY` — Your Google Gemini API Key.
- `ESP_IP` — The local IP address of your ESP32-CAM (e.g., `http://192.168.x.x`).
- `ARDUINO_PORT` — The COM port for your Arduino (e.g., `"COM10"`).

---

## ⚙️ Logic & Deterrent Levels

| Observed Behavior | Danger Level | Hardware Command | Action |
| :--- | :--- | :--- | :--- |
| Normal Shopping | LOW | None | System monitors silently. |
| Shoplifting | LOW | `b` | Triggers a 1s double-buzz warning. |
| Armed Robbery | HIGH | `t` + `b` | Triggers 1.5s Relay Pulse + Buzzer. |

---

## 📜 Detailed File Descriptions

### Core Scripts

- **`proto3.py`** — The **Primary Engine**. Fetches live frames from the ESP32-CAM IP, runs high-frequency AI analysis, and handles the automated hardware escalation logic.
- **`proto2.py`** — Used for **Validation**. Runs the same AI logic against a folder of static images to verify detection accuracy.
- **`proto1.py`** — The **Legacy Prototype**. Contains the initial hardware triggering logic and basic JSON parsing used during early development.

### Utility & Testing

- **`1.py`** — A **Hardware Manual Override**. Manually trigger the Pulse (`ta`) or Buzz (`bu`) commands to verify Arduino wiring without running the AI.
- **`2.py`** — A **Data Tool**. Encodes images to Base64 and outputs structured JSON files for documentation or training purposes.

### Embedded

- **`taser1/taser1.ino`** — The firmware for the Arduino. Listens for characters over Serial and executes the timing logic for the Relay and Buzzer.

---

## 🎬 Media & Demos (Coming Soon)

#### 📺 System Demo
[Link to Demo Video] — *Space reserved for project demonstration*

#### 🛠️ Building the Project (Full Walkthrough)
[Link to Full Tutorial Video] — *Space reserved for build-along guide*

---

## ⚖️ Disclaimer

> *This project is for educational and research purposes only. Ensure compliance with local laws.*
