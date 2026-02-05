#!/usr/bin/env python3
"""
Grove Temperature & Humidity Monitor (Fixed Import)
Author: Yuvraj Singh Palh (Workshop Edition)
"""

import time
import sys
import argparse
import math
# --- FIX: Import 'DHT' instead of the long name ---
from grove.grove_temperature_humidity_sensor import DHT

def get_args():
    """Parses command line arguments for runtime customization."""
    parser = argparse.ArgumentParser(description="Grove DHT Sensor Tester")
    
    # Argument: Digital Port Number (Default D5)
    parser.add_argument(
        '--port', type=int, default=5, 
        help='The Digital Port ID (e.g., 5, 16, 18). Default: 5'
    )
    
    # Argument: Sensor Type
    parser.add_argument(
        '--type', type=str, choices=['blue', 'white'], default='blue',
        help='Sensor color: "blue" (DHT11, default) or "white" (DHT22/Pro)'
    )
    
    # Argument: Unit
    parser.add_argument(
        '--unit', type=str, choices=['C', 'F'], default='C',
        help='Temperature unit: C (Celsius) or F (Fahrenheit)'
    )
    
    # Argument: Interval
    parser.add_argument(
        '--interval', type=float, default=1.5,
        help='Seconds between reads. Default: 1.5'
    )

    return parser.parse_args()

def cel_to_fahr(celsius):
    return (celsius * 9/5) + 32

def main():
    args = get_args()
    
    # --- FIX: Map to strings '11' or '22' for the DHT class ---
    # Blue Sensor = '11', White Sensor = '22'
    sensor_type_map = {'blue': '11', 'white': '22'}
    dht_type = sensor_type_map[args.type]

    print(f"--- 🌡️  Starting Environment Monitor ---")
    print(f"   • Port: D{args.port}")
    print(f"   • Sensor: DHT{dht_type} ({args.type.title()})")
    print("------------------------------------------")

    try:
        # --- FIX: Initialize using the DHT class ---
        # The library expects: DHT(dht_type, pin)
        sensor = DHT(dht_type, args.port)
    except Exception as e:
        print(f"❌ Hardware Init Error: {e}")
        sys.exit(1)

    while True:
        try:
            # The read() method returns (humidity, temperature)
            humidity, temp_c = sensor.read()

            # Skip invalid readings (0, 0 is often returned on error/startup)
            # We also check for NaN just in case
            if math.isnan(temp_c) or math.isnan(humidity):
                continue
            
            # Unit Conversion
            if args.unit == 'F':
                display_temp = cel_to_fahr(temp_c)
                unit_str = "°F"
            else:
                display_temp = temp_c
                unit_str = "°C"

            # Dynamic Status Message
            status = "✅ Normal"
            if temp_c > 30: 
                status = "🔥 HOT"
            elif humidity > 70:
                status = "💧 HUMID"

            # Output formatting
            output = (
                f"Temp: {display_temp:.1f}{unit_str} | "
                f"Humidity: {humidity:.1f}% | "
                f"Status: {status}"
            )
            
            # Print with overwrite
            sys.stdout.write(f"\r{output}   ")
            sys.stdout.flush()

        except Exception as error:
            # DHT sensors frequently throw read errors; we just catch and retry
            pass
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped by user.")
            break

        time.sleep(args.interval)

if __name__ == '__main__':
    main()