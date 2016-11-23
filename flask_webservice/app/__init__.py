import os

from celery import Celery
from config import config, Config

from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

from tasks import long_task

UPLOAD_FOLDER = '/home/andrusza2/temp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config[config_name].init_app(app)

    celery.conf.update(app.config)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'GET':
            return render_template('index.html', email=session.get('email', ''))

        return redirect(url_for('index'))

    # @app.route('/', methods=['GET', 'POST'])
    # def upload_file():
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
    #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #             return redirect(url_for('uploaded_file',
    #                                     filename=filename))
    #     return '''
    #     <!doctype html>
    #     <title>Upload new File</title>
    #     <h1>Upload new File</h1>
    #     <form action="" method=post enctype=multipart/form-data>
    #       <p><input type=file name=file>
    #          <input type=submit value=Upload>
    #     </form>
    #     '''

    @app.route('/longtask', methods=['POST'])
    def longtask():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                task = long_task.apply_async(args=[os.path.join(app.config['UPLOAD_FOLDER'], filename)])
                return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                              task_id=task.id),
                                          'Thumbnail': url_for('uploaded_file',
                                                               filename=filename)
                                          }

                # return redirect(url_for('index'))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''



    @app.route('/upload', methods=['POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''

    @app.route('/status/<task_id>')
    def taskstatus(task_id):
        task = long_task.AsyncResult(task_id)
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

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)

    return app
