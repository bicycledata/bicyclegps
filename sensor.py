import time
import traceback
from collections import deque
from multiprocessing.connection import Connection

import pynmea2
import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

from bicycleinit.BicycleSensor import BicycleSensor


def parse_nmea_sentence(sentence):
  try:
    msg = pynmea2.parse(sentence)
    # Only process RMC sentences
    if msg.sentence_type == 'RMC' and msg.lat_dir+msg.lon_dir in ['NE', 'NW', 'SE', 'SW']:
      return msg.latitude, msg.longitude, msg.lat_dir+msg.lon_dir
  except pynmea2.nmea.ParseError:
      pass
  return None

def main(bicycleinit: Connection, name: str, args: dict):
  sensor = BicycleSensor(bicycleinit, name, args)

  port = args.get('port', '/dev/ttyACM0')
  time_frame = args.get('time_frame', 10)  # seconds
  min_msgs = args.get('min_msgs', 5)

  try:
    ser = serial.Serial(port, baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE, timeout=5.0)
  except serial.SerialException as e:
    sensor.send_msg(f'Error opening serial port {port}: {e}')
    return

  sensor.write_header(['latitude', 'longitude', 'dir'])

  msg_times = deque()
  online = False

  try:
    while True:
      line = ser.readline().decode('ascii', errors='replace').strip()
      gps_data = parse_nmea_sentence(line)
      now = time.time()

      if gps_data is not None:
        sensor.write_measurement(list(gps_data))
        msg_times.append(now)

      # Remove old timestamps
      while msg_times and now - msg_times[0] > time_frame:
        msg_times.popleft()

      # Check online status
      new_online = len(msg_times) >= min_msgs
      if new_online != online:
        online = new_online
        sensor.send_msg({'type': 'status', 'online': online})
  except KeyboardInterrupt:
    pass
  except Exception as e:
    sensor.send_msg({'type': 'log', 'level': 'error', 'msg': str(e)})
    sensor.send_msg({'type': 'log', 'level': 'error', 'msg': traceback.format_exc()})
  finally:
    ser.close()
    sensor.shutdown()

if __name__ == "__main__":
  main(None, "bicyclegps", {'port': '/dev/ttyACM0'})
