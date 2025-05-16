#!/usr/bin/env python3

import argparse
import time

import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

import NMEA0183
from BicycleSensor import BicycleSensor, setup_logging


class BicycleGPS(BicycleSensor):
  def write_header(self):
    return 'time, gps_time, latitude, longitude, altitude'

  def write_measurement(self):
    self.data_buffer.append(f'{str(time.time())}, {self._gps_time}, {self._latitude}, {self._longitude}, {self._altitude}')

  def worker_main(self):
    self._gps_time = None
    self._latitude = None
    self._longitude = None
    self._altitude = None

    def worker():
      with serial.Serial('/dev/serial0', baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE) as ser:
        ser.readline() # trash first line

        while self.alive:
          try:
            sentence = NMEA0183.bytes_to_sentence(ser.readline())
          except Exception as e:
            pass
          except KeyboardInterrupt:
            pass
          else:
            if sentence.topic == b'RMC':
              try:
                rmc = NMEA0183.RMC(sentence)
              except Exception:
                pass
              else:
                self._gps_time = rmc.time
                self._latitude = rmc.latitude
                self._longitude = rmc.longitude
            elif sentence.topic == b'GGA':
              try:
                gga = NMEA0183.GGA(sentence)
              except Exception:
                pass
              else:
                self._altitude = gga.altitude
    return worker


if __name__ == '__main__':
  PARSER = argparse.ArgumentParser(
    description='Sensor Template',
    allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  PARSER.add_argument('--hash', type=str, required=True, help='[required] hash of the device')
  PARSER.add_argument('--name', type=str, required=True, help='[required] name of the sensor')
  PARSER.add_argument('--loglevel', type=str, default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING)')
  PARSER.add_argument('--measurement-frequency', type=float, default=1.0, help='Frequency of sensor measurements in 1/s')
  PARSER.add_argument('--stdout', action='store_true', help='Enables logging to stdout')
  PARSER.add_argument('--upload-interval', type=float, default=300.0, help='Interval between uploads in seconds')
  ARGS = PARSER.parse_args()

  # Configure logging
  setup_logging('bicyclegps.log', stdout=ARGS.stdout, rotating=True, loglevel=ARGS.loglevel)

  sensor = BicycleGPS(ARGS.name, ARGS.hash, ARGS.measurement_frequency, ARGS.upload_interval)
  sensor.main()
