import traceback
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

  try:
    ser = serial.Serial(port, baudrate=4800, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE, timeout=5.0)
  except serial.SerialException as e:
    sensor.send_msg(f'Error opening serial port {port}: {e}')
    return

  sensor.write_header(['latitude', 'longitude', 'dir'])

  try:
    while True:
      line = ser.readline().decode('ascii', errors='replace').strip()
      gps_data = parse_nmea_sentence(line)

      if gps_data is not None:
        sensor.write_measurement(list(gps_data))

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
