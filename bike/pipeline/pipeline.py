import os, sys
import uuid
import pandas as pd
from threading import Thread
from bike.constant import *
from bike.logger import logging
from bike.exception import BikeException
from bike.config.configuration import Configuration
from bike.entity.config_entity import *
from bike.entity.artifact_entity import *
from bike.component.data_ingestion import DataIngestion


class Pipeline:
    def __init__(self, config: Configuration = Configuration()) -> None:
        try:
            self.config = config
        except Exception as e:
            raise BikeException(e, sys) from e

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise BikeException(e, sys) from e

    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
        except Exception as e:
            raise BikeException(e, sys) from e
