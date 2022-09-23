from flask import Flask, request
import sys

import pip
from bike.util.util import read_yaml_file, write_yaml_file
from matplotlib.style import context
from bike.logger import logging
from bike.exception import BikeException
import os, sys
import json
from bike.config.configuration import Configuration
from bike.constant import CONFIG_DIR, get_current_time_stamp
from bike.pipeline.pipeline import Pipeline
from bike.entity.bike_predictor import BikePredictor, BikeData
from flask import send_file, abort, render_template
from bike.logger import get_log_dataframe

ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "logs"
PIPELINE_FOLDER_NAME = "bike"
SAVED_MODELS_DIR_NAME = "saved_models"
BATCH_DATA = 'hours.csv'
MODEL_CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, "model.yaml")
LOG_DIR = os.path.join(ROOT_DIR, LOG_FOLDER_NAME)
PIPELINE_DIR = os.path.join(ROOT_DIR, PIPELINE_FOLDER_NAME)
MODEL_DIR = os.path.join(ROOT_DIR, SAVED_MODELS_DIR_NAME)
SHARING_DATA_KEY = "bike_data"
MEDIAN_SHARING_VALUE_KEY = "median_bike_value"

app = Flask(__name__)


@app.route('/artifact', defaults={'req_path': 'bike'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    os.makedirs("bike", exist_ok=True)
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print("abs_path", abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        if ".html" in abs_path:
            with open(abs_path, "r", encoding="utf-8") as file:
                content = ''
                for line in file.readlines():
                    content = f"{content}{line}"
                return content
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file_name): file_name for file_name in os.listdir(abs_path) if
             "artifact" in os.path.join(abs_path, file_name)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('files.html', result=result)


@app.route("/", methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        sharing = BikeException(e, sys)
        logging.info(sharing.error_message)


@app.route('/view_experiment_hist', methods=['GET', 'POST'])
def view_experiment_history():
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    experiment_df = pipeline.get_experiments_status()
    context = {
        "experiment": experiment_df.to_html(classes='table table-striped col-12')
    }
    return render_template('experiment_history.html', context=context)


@app.route('/train', methods=['GET', 'POST'])
def train():
    message = ""
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    if not Pipeline.experiment.running_status:
        message = "Training started."
        pipeline.start()
    else:
        message = "Training is already in progress."
    context = {
        "experiment": pipeline.get_experiments_status().to_html(classes='table table-striped col-12'),
        "message": message
    }
    return render_template('train.html', context=context)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    try:

        context = {
            SHARING_DATA_KEY: None,
            MEDIAN_SHARING_VALUE_KEY: None
        }

        if request.method == 'POST':
            season = int(request.form['season'])
            year = int(request.form['year'])
            month = int(request.form['month'])
            hour = int(request.form['hour'])
            holiday = int(request.form['holiday'])
            weekday = int(request.form['weekday'])
            workingday = int(request.form['workingday'])
            weather = int(request.form['weather'])
            temp = float(request.form['temp'])
            humidity = float(request.form['humidity'])
            windspeed = float(request.form['windspeed'])
            print(season, year, month, hour, holiday, weekday, workingday, weather, temp, humidity, windspeed)
            sharing_data = BikeData(season=season,
                                    year=year, month=month, hour=hour, holiday=holiday, weekday=weekday,
                                    workingday=workingday, weather=weather, temp=temp,
                                    humidity=humidity, windspeed=windspeed)
            sharing_df = sharing_data.get_bike_input_data_frame()
            sharing_predictor = BikePredictor(model_dir=MODEL_DIR)
            median_sharing_value = sharing_predictor.predict(X=sharing_df)
            context = {
                SHARING_DATA_KEY: sharing_data.get_bike_data_as_dict(),
                MEDIAN_SHARING_VALUE_KEY: int(median_sharing_value),
            }
            return render_template('predict.html', context=context)
        return render_template("predict.html", context=context)

    except Exception as e:
        raise BikeException(e, sys) from e


@app.route('/saved_models', defaults={'req_path': 'saved_models'})
@app.route('/saved_models/<path:req_path>')
def saved_models_dir(req_path):
    os.makedirs("saved_models", exist_ok=True)
    # Joining the base and the requested path
    abs_path = os.path.join(req_path)
    # Return 404 if path doesn't exist

    if not os.path.exists(abs_path):
        return abort(404)

        # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('saved_models_files.html', result=result)


@app.route("/update_model_config", methods=['GET', 'POST'])
def update_model_config():
    try:
        if request.method == 'POST':
            model_config = request.form['new_model_config']
            model_config = model_config.replace("'", '"')
            model_config = json.loads(model_config)

            write_yaml_file(file_path=MODEL_CONFIG_FILE_PATH, data=model_config)

        model_config = read_yaml_file(file_path=MODEL_CONFIG_FILE_PATH)
        return render_template('update_model.html', result={"model_config": model_config})

    except Exception as e:
        logging.exception(e)
        return str(e)


@app.route(f'/logs', defaults={'req_path': f'{LOG_FOLDER_NAME}'})
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')
def render_log_dir(req_path):
    os.makedirs(LOG_FOLDER_NAME, exist_ok=True)
    # Joining the base and the requested path
    logging.info(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        log_df = get_log_dataframe(abs_path)
        context = {"log": log_df.to_html(classes="table-striped", index=False)}
        return render_template('log.html', context=context, dashboard=False)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('log_files.html', result=result, dashboard=False)
