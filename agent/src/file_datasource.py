from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        parking_filename: str
    ) -> None:
        self.accelerometer_file = accelerometer_filename
        self.gps_file = gps_filename
        self.parking_file = parking_filename

        self.accelerometer_data = []
        self.gps_data = []
        self.parking_data = []

        self.accelerometer_index = 0
        self.gps_index = 0
        self.parking_index = 0

        self.stopped = False
    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        if self.stopped:
            return None

        accelerometer_line = self.accelerometer_data[self.accelerometer_index]
        gps_line = self.gps_data[self.gps_index]
        parking_line = self.parking_data[self.parking_index]

        accelerometer_data = list(map(float, accelerometer_line))
        gps_data = list(map(float, gps_line))
        parking_data = list(map(float, parking_line))

        self.accelerometer_index = (self.accelerometer_index + 1) % len(self.accelerometer_data)
        self.gps_index = (self.gps_index + 1) % len(self.gps_data)
        self.parking_index = (self.parking_index + 1) % len(self.parking_data)

        self.stopReading()

        return AggregatedData(
            Accelerometer(*accelerometer_data),
            Gps(*gps_data),
            Parking(parking_data[0], Gps(parking_data[1], parking_data[2])),
            datetime.now(),
            config.USER_ID,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        with open(self.accelerometer_file, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)
            self.accelerometer_data = list(csv_reader)

        with open(self.gps_file, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)
            self.gps_data = list(csv_reader)

        with open(self.parking_file, 'r') as file:
            csv_reader = reader(file)
            next(csv_reader)
            self.parking_data = list(csv_reader)

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        if self.gps_index != 0 or self.accelerometer_index != 0 or self.parking_index != 0:
            return
        self.stopped = True
