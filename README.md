# Sensor Template

## Overview

The `sensor_template` repository provides a robust framework for
implementing a custom bicycle sensor. The framework handles file
system operations, including the creation and management of data
files, and automates the upload of sensor measurements to a remote
server. This allows developers to focus on their custom sensor logic
by extending the provided `BicycleSensor` class and implementing the
necessary methods.

## Features

- **File System Management**: Automatically creates directories and
  manages data files for storing sensor measurements.
- **Automated Data Upload**: Periodically uploads sensor data to a
  configured remote server, with customizable upload intervals.
- **Customizable Sensor Logic**: Developers can create custom sensors
  by extending the `BicycleSensor` class and implementing specific
  methods for data handling.
- **Logging**: Configurable logging with options for file-based
  logging, rotating logs, and console output.

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure you have Python 3 installed on your system.
- **Dependencies**: The framework uses the `requests` module for
  handling HTTP requests. You can install it using:

```bash
pip install requests
```

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/bicycledata/sensor_template.git
cd sensor_template
```

### Usage

To create a custom bicycle sensor, extend the `BicycleSensor` class
and implement the abstract methods: `write_header()` and
`write_measurement()`. The provided `SensorTemplate` class serves as
an example implementation that records the current time as a sensor
measurement.

Example:

```python
class MyCustomSensor(BicycleSensor):
    def write_header(self):
        self.write_to_file('time, speed')

    def write_measurement(self):
        speed = get_speed_data()  # Replace with actual sensor logic
        self.write_to_file(f"{time.time()}, {speed}")
```

### Example Usage

You can run the provided `SensorTemplate` class with the following
command:

```bash
./sensor.py --hash <device_hash> --name <sensor_name> [options]
```

### Command-Line Arguments

- `--hash` (required): The unique hash of the device, used for
  identifying the sensor during uploads.
- `--name` (required): The name of the sensor.
- `--loglevel` (optional): Set the logging level (`DEBUG`, `INFO`,
  `WARNING`). Default is `INFO`.
- `--measurement-frequency` (optional): Frequency of sensor
  measurements in Hertz (measurements per second). Default is `1.0
  Hz`.
- `--stdout` (optional): Enable logging output to the console
  (stdout).
- `--upload-interval` (optional): Interval between data uploads in
  seconds. Default is `300 seconds` (5 minutes).

### Framework Details

The framework handles the following operations:

- **File Management**: Data is written to CSV files stored in the
  `pending` directory. Upon successful upload, files are moved to the
  `uploaded` directory.
- **Data Upload**: Data is uploaded to a remote server (configured in
  the `_upload_data` method) using HTTP POST requests. The upload
  logic is executed in a separate thread to ensure that the main
  sensor loop runs without interruptions.
- **Signal Handling**: The framework gracefully handles shutdown
  signals (`SIGTERM`, `SIGINT`) and ensures that any pending data is
  uploaded before exiting.

### Logging

Logging is configured through the `configure()` function. The
framework supports:

- **File-based logging**: Logs are stored in the
  `log/sensor_template.log` file.
- **Rotating logs**: By enabling the `rotating` option, logs are
  rotated when they reach 5MB in size, with a backup count of 2.
- **Console output**: Enable logging to the console using the
  `--stdout` flag.

### Data Upload

The framework's automated upload feature sends sensor data to the
server at regular intervals. The upload process is managed by a
separate thread, ensuring it does not interfere with data collection.
The upload endpoint and payload are defined in the `_upload_data()`
method.

**Note**: If the upload fails, the data remains in the `pending`
directory and the framework retries in the next cycle.

## Contributing

Contributions are welcome! If you have suggestions for improvements or
find any bugs, feel free to open an issue or submit a pull request.

## License

This repository is licensed under the MIT License. See the `LICENSE` file for more details.
