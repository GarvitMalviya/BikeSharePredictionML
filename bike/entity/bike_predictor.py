import os
import sys

from bike.exception import BikeException
from bike.util.util import load_object

import pandas as pd


class BikeData:
    def __init__(self,
                 season: int,
                 year: int,
                 month: int,
                 hour: int,
                 holiday: int,
                 weekday: int,
                 workingday: int,
                 weather: int,
                 temp: float,
                 humidity: float,
                 windspeed: float) -> None:
        try:
            self.season = season
            self.year = year
            self.month = month
            self.hour = hour
            self.holiday = holiday
            self.weekday = weekday
            self.workingday = workingday
            self.weather = weather
            self.temp = temp
            self.humidity = humidity
            self.windspeed = windspeed
        except Exception as e:
            raise BikeException(e, sys) from e

    def get_bike_input_data_frame(self):
        try:
            sharing_input_dict = self.get_bike_data_as_dict()
            return pd.DataFrame(sharing_input_dict)
        except Exception as e:
            raise BikeException(e, sys) from e

    def get_bike_data_as_dict(self):
        try:
            input_data = {
                "season": [self.season],
                "year": [self.year],
                "month": [self.month],
                "hour": [self.hour],
                "holiday": [self.holiday],
                "weekday": [self.weekday],
                "workingday": [self.workingday],
                "weather": [self.weather],
                "temp": [self.temp],
                "humidity": [self.humidity],
                "windspeed": [self.windspeed],
            }
            return input_data
        except Exception as e:
            raise BikeException(e, sys)


class BikePredictor:

    def __init__(self, model_dir: str):
        try:
            self.model_dir = model_dir
        except Exception as e:
            raise BikeException(e, sys) from e

    def get_latest_model_path(self):
        try:
            folder_name = list(map(int, os.listdir(self.model_dir)))
            # print("FOLDER NAME",folder_name)
            latest_model_dir = os.path.join(self.model_dir, f"{max(folder_name)}")
            # print("lateset_model ", latest_model_dir)
            file_name = os.listdir(latest_model_dir)[0]
            latest_model_path = os.path.join(latest_model_dir, file_name)
            # self.s3_download_model()
            return latest_model_path
        except Exception as e:
            raise BikeException(e, sys) from e

    def predict(self, X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            median_house_value = model.predict(X)
            return median_house_value
        except Exception as e:
            raise BikeException(e, sys) from e
