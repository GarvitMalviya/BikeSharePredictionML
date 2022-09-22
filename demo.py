from bike.constant import *
from bike.logger import logging
from bike.pipeline.pipeline import Pipeline
from bike.exception import BikeException
import sys, os


def main():
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
    except Exception as e:
        raise BikeException(e, sys) from e


if __name__ == "__main__":
    main()
