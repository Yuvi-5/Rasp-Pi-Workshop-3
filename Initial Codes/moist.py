#!/usr/bin/env python3
"""
Grove Moisture Sensor Monitor 
Author: Yuvraj Singh Palh
"""

import time
import sys
import argparse
from grove.grove_moisture_sensor import GroveMoistureSensor

def get_args():
    parser = argparse.ArgumentParser(description="Grove Moisture Sensor Tester")
    parser.add_argument(
        '--port', type=int, default=0, 
        help='The Analog Port ID (0 for A0, 2 for A2). Default: 0'
    )
    parser.add_argument(
        '--interval', type=float, default=0.5,
        help='Seconds between reads. Default: 0.5'
    )
    return parser.parse_args()

def get_status(value):
    # 0-300: Dry, 300-600: Moist, 600+: Wet
    if value < 300:
        return "🌵 DRY"
    elif value < 600:
        return "🌱 MOIST"
    else:
        return "🌊 WET"

def draw_bar(value, max_val=1000, width=20):
    # Clamp value to max
    value = min(value, max_val)
    fill = int((value / max_val) * width)
    bar = '█' * fill + '-' * (width - fill)
    return f"[{bar}]"

def main():
    args = get_args()

    print(f"--- 💧 Starting Moisture Monitor ---")
    print(f"   • Port: A{args.port}")
    print("------------------------------------------")

    try:
        # Initialize Sensor
        sensor = GroveMoistureSensor(args.port)
    except Exception as e:
        print(f"❌ Hardware Init Error: {e}")
        sys.exit(1)

    while True:
        try:
            # --- FIX: Use .moisture property, NOT .read() ---
            # It is a variable, not a function, so no brackets ()
            moisture = sensor.moisture

            status = get_status(moisture)
            bar_graph = draw_bar(moisture)

            output = (
                f"Level: {moisture:<4} "
                f"{bar_graph} "
                f"Status: {status}"
            )
            
            sys.stdout.write(f"\r{output}   ")
            sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n\n🛑 Monitor stopped.")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")

        time.sleep(args.interval)

if __name__ == '__main__':
    main()