"""
Main application module.
Flask application business logic.
"""

import os
import time

from celery import Celery
from config import config, Config

from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, send_from_directory
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

from tasks import prediction_task, extract_first_frame


VIDEO_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


def is_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in VIDEO_EXTENSIONS


def create_app(config_name):
    app = Flask(__name__)
    api = Api(app)
    app.config.from_object(config[config_name])
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config[config_name].init_app(app)

    celery.conf.update(app.config)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'GET':
            return render_template('index.html')

        return redirect(url_for('index'))

    # @app.route('/longtask', methods=['POST'])
    # def longtask():
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('No file part')
    #             return redirect(request.url)
    #         file = request.files['file']
    #         # if user does not select file, browser also
    #         # submit a empty part without filename
    #         if file.filename == '':
    #             flash('No selected file')
    #             return redirect(request.url)
    #         if file and allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             dot_index = filename.index('.')
    #             filename = filename[:dot_index] + '_' + repr(int(round(time.time()))) + filename[dot_index:]
    #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #
    #             if(is_video(file.filename)):
    #                 filename = extract_first_frame(filename)
    #
    #             task = prediction_task.apply_async(args=[os.path.join(app.config['UPLOAD_FOLDER'], filename)])
    #
    #             return jsonify({}), 202, {'Location': url_for('taskstatus',
    #                                                           task_id=task.id),
    #                                       'Thumbnail': url_for('uploaded_file',
    #                                                            filename=filename)
    #                                       }
    #
    #     return '''
    #     <!doctype html>
    #     <title>Upload new File</title>
    #     <h1>Upload new File</h1>
    #     <form action="" method=post enctype=multipart/form-data>
    #       <p><input type=file name=file>
    #          <input type=submit value=Upload>
    #     </form>
    #     '''

    class RestApi(Resource):
        def get(self):
            return {"info": "Prediction Popularity WebAPI",
                    "author": "Pawel Andruszkiewicz",
                    "services": [{"predict": url_for("predict", _external=True)}]}

    api.add_resource(RestApi, '/api')


    class Predict(Resource):
        # def get(self):
        #     return {"error": "Method not allowed"}

        def post(self):
            if 'file' not in request.files:
                return {"error": "No file in request. Request should contain image or video file."}

            file = request.files['file']

            if file.filename == '':
                return {"error": "File has no name."}

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                dot_index = filename.index('.')
                filename = filename[:dot_index] + '_' + repr(int(round(time.time()))) + filename[dot_index:]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                if(is_video(file.filename)):
                    filename = extract_first_frame(filename)

                task = prediction_task.apply_async(args=[os.path.join(app.config['UPLOAD_FOLDER'], filename)])

                return {'location': url_for('taskstatus',
                                                              task_id=task.id, _external=True),
                                          'thumbnail': url_for('uploaded_file',
                                                               filename=filename, _external=True)
                                          }
            else:
                return {'error': 'Unsupported file.'}

    api.add_resource(Predict, '/api/predict')


    class TaskStatus(Resource):
        def get(self, task_id):
            task = prediction_task.AsyncResult(task_id)
            if task.state == 'PENDING':
                response = {
                    'state': task.state,
                    'current': 0,
                    'total': 1,
                    'status': 'Pending...'
                }
            elif task.state != 'FAILURE':
                response = {
                    'state': task.state,
                    'current': task.info.get('current', 0),
                    'total': task.info.get('total', 1),
                    'status': task.info.get('status', '')
                }
                if 'result' in task.info:
                    response['result'] = task.info['result']
            else:
                # something went wrong in the background job
                response = {
                    'state': task.state,
                    'current': 1,
                    'total': 1,
                    'status': str(task.info),  # this is the exception raised
                }
            return jsonify(response)

    api.add_resource(TaskStatus, '/api/status/<task_id>')

    # @app.route('/status/<task_id>')
    # def taskstatus(task_id):
    #     task = prediction_task.AsyncResult(task_id)
    #     if task.state == 'PENDING':
    #         response = {
    #             'state': task.state,
    #             'current': 0,
    #             'total': 1,
    #             'status': 'Pending...'
    #         }
    #     elif task.state != 'FAILURE':
    #         response = {
    #             'state': task.state,
    #             'current': task.info.get('current', 0),
    #             'total': task.info.get('total', 1),
    #             'status': task.info.get('status', '')
    #         }
    #         if 'result' in task.info:
    #             response['result'] = task.info['result']
    #     else:
    #         # something went wrong in the background job
    #         response = {
    #             'state': task.state,
    #             'current': 1,
    #             'total': 1,
    #             'status': str(task.info),  # this is the exception raised
    #         }
    #     return jsonify(response)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)


    return app
