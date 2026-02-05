import time
import psutil
import socketio
import requests
import sys

# ==============================================================================
# ⚙️  HARDWARE CONFIGURATION (STUDENT SECTION)
# ==============================================================================
# INSTRUCTIONS:
# - Enter the Port Number (integer) if connected.
# - Set to None (no quotes) if NOT using that sensor.
# - Example: MOISTURE_PORT = 0  (for A0)

# --- SERVER SETTINGS ---
SERVER_IP   = 'http://192.168.137.1:5000'  # CHECK WHITEBOARD FOR IP
TEAM_NAME   = 'Team Alpha'                 # CHANGE THIS
NODE_ID     = 'Pi-1'                      # UNIQUE ID

# --- SENSORS (INPUTS) ---
MOISTURE_PORT = 'None'         # Port A0
LIGHT_PORT    = 'None'         # Port A2
DHT_PORT      = 'None'         # Port D5 (Blue Sensor)

# --- ACTUATORS (OUTPUTS) ---
LED_PORT      = 'None'        # Port D16
BUZZER_PORT   = 'None'        # Port D18
DISPLAY_PORT  = 'None'     # Keep as 'I2C' if using LCD

# ==============================================================================
# 🛠️ SYSTEM INITIALIZATION
# ==============================================================================
sio = socketio.Client()
sensors = {}
actuators = {}

# Helper to sanitize input (in case students type 'None' as a string)
def clean_port(p):
    if str(p).lower() == 'none' or p == '': return None
    return p

MOISTURE_PORT = clean_port(MOISTURE_PORT)
LIGHT_PORT = clean_port(LIGHT_PORT)
DHT_PORT = clean_port(DHT_PORT)
LED_PORT = clean_port(LED_PORT)
BUZZER_PORT = clean_port(BUZZER_PORT)

print("--------------------------------------")
print(f"🚀 INITIALIZING EDGE NODE: {TEAM_NAME}")
print("--------------------------------------")

try:
    # --- IMPORTS BASED ON YOUR WORKING SCRIPTS ---
    from grove.grove_moisture_sensor import GroveMoistureSensor
    from grove.grove_light_sensor_v1_2 import GroveLightSensor
    from grove.grove_temperature_humidity_sensor import DHT  # <--- UPDATED IMPORT
    from grove.gpio import GPIO                              # <--- UPDATED FOR LED/BUZZ
    from grove.display.jhd1802 import JHD1802 

    # 1. Moisture (A0)
    if MOISTURE_PORT is not None:
        sensors['moisture'] = GroveMoistureSensor(MOISTURE_PORT)
        print(f"✅ Moisture Sensor active on Port A{MOISTURE_PORT}")

    # 2. Light (A2)
    if LIGHT_PORT is not None:
        sensors['light'] = GroveLightSensor(LIGHT_PORT)
        print(f"✅ Light Sensor active on Port A{LIGHT_PORT}")

    # 3. DHT Temp/Humid (D5) - Fixed for DHT11 (Blue)
    if DHT_PORT is not None:
        sensors['dht'] = DHT('11', DHT_PORT)
        print(f"✅ DHT11 Sensor active on Port D{DHT_PORT}")

    # 4. LED (D16) - Using GPIO
    if LED_PORT is not None:
        actuators['led'] = GPIO(LED_PORT, GPIO.OUT)
        print(f"✅ LED Ready on Port D{LED_PORT}")

    # 5. Buzzer (D18) - Using GPIO
    if BUZZER_PORT is not None:
        actuators['buzzer'] = GPIO(BUZZER_PORT, GPIO.OUT)
        print(f"✅ Buzzer Ready on Port D{BUZZER_PORT}")

    # 6. LCD Display (I2C)
    if DISPLAY_PORT is not None:
        actuators['lcd'] = JHD1802()
        print(f"✅ LCD Display Ready on I2C")

except ImportError:
    print("⚠️  CRITICAL: Grove Libraries missing. Run 'pip install grove.py'")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Hardware Init Error: {e}")

# ==============================================================================
# 📡 TELEMETRY LOGIC
# ==============================================================================

def get_pi_stats():
    """Reads internal CPU stats."""
    cpu = psutil.cpu_percent(interval=None)
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = round(int(f.read()) / 1000.0, 1)
    except: temp = 0.0
    
    # Measure Latency
    try:
        start = time.time()
        requests.get(SERVER_IP, timeout=0.5)
        ping = int((time.time() - start) * 1000)
    except: ping = 999
    return cpu, temp, ping

def read_environment():
    """Reads configured sensors."""
    data = {}
    
    # Moisture (.moisture property)
    if 'moisture' in sensors:
        data['moisture'] = sensors['moisture'].moisture
    
    # Light (.light property)
    if 'light' in sensors:
        data['light'] = sensors['light'].light
        
    # DHT (returns humidity, temperature)
    if 'dht' in sensors:
        try:
            h, t = sensors['dht'].read()
            data['env_temp'] = t
            data['env_humidity'] = h
        except: pass
            
    return data

# ==============================================================================
# 🔄 MAIN LOOP
# ==============================================================================
try:
    print(f"📡 Connecting to Dashboard at {SERVER_IP}...")
    sio.connect(SERVER_IP)
    print(f"🟢 ONLINE. Streaming Data...")

    while True:
        # 1. Gather Data
        cpu, sys_temp, ping = get_pi_stats()
        env_data = read_environment()
        
        # 2. Package & Send
        payload = {
            'id': NODE_ID,
            'name': TEAM_NAME,
            'cpu': cpu,
            'temp': sys_temp,
            'latency': ping,
            **env_data
        }
        sio.emit('telemetry_stream', payload)
        
        # Print for local debugging
        print(f"Sent: {payload}")

        # ======================================================================
        # 🎓 STUDENT ZONE: AUTOMATION LOGIC
        # ======================================================================
        # INSTRUCTIONS:
        # 1. Use env_data['moisture'], env_data['env_temp'], etc. to check values.
        # 2. Use actuators['led'].write(1) to turn ON, .write(0) to turn OFF.
        # 3. Use actuators['lcd'].setCursor(0,0) and .write("Text") for screen.
        
        # --- TASK 1: UPDATE SCREEN ---
        # (Write your LCD code here...)
        
        
        
        # --- TASK 2: ALERTS ---
        # (Write your if/else logic for LED & Buzzer here...)
        
        
        
        # ======================================================================
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Node Stopped.")
    sio.disconnect()
    # Turn off LED on exit if exists
    if 'led' in actuators: actuators['led'].write(0)
    if 'buzzer' in actuators: actuators['buzzer'].write(0)
    if 'lcd' in actuators: actuators['lcd'].clear()