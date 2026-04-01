// Parth's serial-pulsed relay 2

const int RELAY2_PIN = 8;     
const int buzzer = 9;
const unsigned long PULSE_TIME = 1500/2;  // 1.5 seconds in ms (/2)

void setup() {
  Serial.begin(9600);
  pinMode(RELAY2_PIN, OUTPUT);
  digitalWrite(RELAY2_PIN, HIGH);  // start OFF (change to HIGH if active‑low)

  pinMode(buzzer, OUTPUT);
}

void loop() {
  // If any data is available on Serial, trigger a pulse
  if (Serial.available() > 0) {        // check if something arrived[web:16]
    
    char c = Serial.read();

    if (c=='t'){
      // Turn relay ON
      digitalWrite(RELAY2_PIN, LOW);    // for active‑high relay[web:21]
      Serial.println("Relay 2: ON");
      delay(PULSE_TIME);                 // keep it ON for 1.5 seconds[web:30]

      // Turn relay OFF
      digitalWrite(RELAY2_PIN, HIGH);
      Serial.println("Relay 2: OFF");
    }

    if (c=='b'){
      Serial.println("Buzzer Double Sound: ON");
      tone(buzzer, 1000); // Send 1KHz sound signal...
      delay(1000);        // ...for 1 sec
      noTone(buzzer);     // Stop sound...
      delay(1000);        // ...for 1sec
      tone(buzzer, 1000); // Send 1KHz sound signal...
      delay(1000);        // ...for 1 sec
      noTone(buzzer);     // Stop sound...
      Serial.println("Buzzer Double Sound: OFF");
    }


  }
}
