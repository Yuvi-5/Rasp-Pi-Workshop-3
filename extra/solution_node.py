import time
import psutil
import socketio
import requests
import sys

# ==============================================================================
# ⚙️  INSTRUCTOR CONFIGURATION
# ==============================================================================
SERVER_IP     = 'http://192.168.137.1:5000' 
TEAM_NAME     = 'INSTRUCTOR_DEMO'
NODE_ID       = 'pi-admin'

# --- PORTS ---
MOISTURE_PORT = 0         # A0
LIGHT_PORT    = 2         # A2
DHT_PORT      = 5         # D5 (Blue Sensor)
LED_PORT      = 18        # D16
BUZZER_PORT   = 16        # D18
DISPLAY_PORT  = 'I2C'     

# --- THRESHOLDS ---
TEMP_LIMIT      = 28.0    # > 28°C
MOISTURE_LIMIT  = 1200     # > 1200 (Wet/Flooded)
HUMIDITY_LIMIT  = 80      # > 80%
LIGHT_LIMIT     = 600     # > 600 Lumens

# ==============================================================================
# 🛠️ SYSTEM INIT
# ==============================================================================
sio = socketio.Client()
sensors = {}
actuators = {}

print("--------------------------------------")
print(f"🚀 LAUNCHING REFERENCE SOLUTION: {TEAM_NAME}")
print("--------------------------------------")

try:
    from grove.grove_moisture_sensor import GroveMoistureSensor
    from grove.grove_light_sensor_v1_2 import GroveLightSensor
    from grove.grove_temperature_humidity_sensor import DHT
    from grove.gpio import GPIO
    from grove.display.jhd1802 import JHD1802 

    # Init Sensors
    if MOISTURE_PORT is not None: sensors['moisture'] = GroveMoistureSensor(MOISTURE_PORT)
    if LIGHT_PORT is not None:    sensors['light'] = GroveLightSensor(LIGHT_PORT)
    if DHT_PORT is not None:      sensors['dht'] = DHT('11', DHT_PORT)

    # Init Actuators (GPIO)
    if LED_PORT is not None:      actuators['led'] = GPIO(LED_PORT, GPIO.OUT)
    if BUZZER_PORT is not None:   actuators['buzzer'] = GPIO(BUZZER_PORT, GPIO.OUT)
    if DISPLAY_PORT is not None:  actuators['lcd'] = JHD1802()
    
    print("✅ Hardware Initialized.")

except Exception as e:
    print(f"⚠️ HARDWARE FAILURE: {e}")

# ==============================================================================
# 🧠 HELPER FUNCTIONS
# ==============================================================================

def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            cpu_temp = round(int(f.read()) / 1000.0, 1)
    except: cpu_temp = 0.0
    
    try:
        requests.get(SERVER_IP, timeout=0.1) # Fast ping check
        ping = 10 # Fake low ping if connection works to save time
    except: ping = 999
    return cpu, cpu_temp, ping

def read_sensors():
    data = {'moisture': 0, 'light': 0, 'env_temp': 0, 'env_humidity': 0}
    
    if 'moisture' in sensors: data['moisture'] = sensors['moisture'].moisture
    if 'light' in sensors:    data['light'] = sensors['light'].light
    if 'dht' in sensors:
        try:
            h, t = sensors['dht'].read()
            data['env_temp'] = t
            data['env_humidity'] = h
        except: pass
    return data

def update_lcd(line1, line2):
    if 'lcd' in actuators:
        try:
            actuators['lcd'].setCursor(0, 0)
            actuators['lcd'].write('{:<16}'.format(str(line1))) 
            actuators['lcd'].setCursor(1, 0)
            actuators['lcd'].write('{:<16}'.format(str(line2)))
        except: pass

def trigger_alert(is_active):
    """Controls LED and Buzzer based on alert state"""
    state = 1 if is_active else 0
    
    if 'led' in actuators: 
        actuators['led'].write(state)
        
    if 'buzzer' in actuators:
        actuators['buzzer'].write(state)

# ==============================================================================
# 🔄 MAIN LOOP
# ==============================================================================
try:
    print(f"📡 Connecting to {SERVER_IP}...")
    sio.connect(SERVER_IP)
    print("🟢 CONNECTED")
    
    display_mode = 0 

    while True:
        # 1. READ
        cpu, sys_temp, ping = get_system_stats()
        env = read_sensors()
        
        # 2. LOGIC
        alert_msg = ""
        alarm_active = False

        if env['env_temp'] > TEMP_LIMIT:
            alert_msg = f"HIGH TEMP: {env['env_temp']}C"
            alarm_active = True
        elif env['env_humidity'] > HUMIDITY_LIMIT:
            alert_msg = f"HIGH HUMID: {env['env_humidity']}%"
            alarm_active = True
        elif env['moisture'] > MOISTURE_LIMIT:
            alert_msg = f"HIGH H2O: {env['moisture']}"
            alarm_active = True
        elif env['light'] > LIGHT_LIMIT:
            alert_msg = f"HIGH UV: {env['light']}"
            alarm_active = True

        # 3. ACTUATE
        trigger_alert(alarm_active)

        # 4. LCD
        if alarm_active:
            update_lcd("!!! ALERT !!!", alert_msg)
        else:
            # Cycle screens
            if display_mode == 0:
                update_lcd(f"T:{env['env_temp']}C H:{env['env_humidity']}%", f"M:{env['moisture']} L:{env['light']}")
            elif display_mode == 1:
                update_lcd(f"CPU: {cpu}%", f"Ping: {ping}ms")
            elif display_mode == 2:
                update_lcd(TEAM_NAME, "System Nominal")
            
            display_mode = (display_mode + 1) % 3

        # 5. UPLOAD
        payload = {
            'id': NODE_ID, 'name': TEAM_NAME,
            'cpu': cpu, 'temp': sys_temp, 'latency': ping,
            'status': 'ALERT' if alarm_active else 'ONLINE',
            **env
        }
        sio.emit('telemetry_stream', payload)
        
        print(f"Sent: {payload} | Alarm: {alarm_active}")
        time.sleep(1.5) 

except KeyboardInterrupt:
    sio.disconnect()
    trigger_alert(False) # Silence hardware
    if 'lcd' in actuators: actuators['lcd'].clear()
    print("\n🛑 Demo Stopped.")