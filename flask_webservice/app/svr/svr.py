# set up Python environment: numpy for numerical routines...
import numpy as np
import pickle
from faster_rcnn_feature_extractor import Predictor

predictor = None


def getPredictor():
    global predictor

    if predictor is None:
        predictor = Predictor()

    return predictor


clf = pickle.load(open("app/svr/svr_test_pref_26.10.sk", 'rb'))


def predict(imgpath, task=None):
    if (task):
        task.update_state(state='PROGRESS',meta={'current': 10 , 'total': 100, 'status': "Getting neural network feature extractor"})
    feature_vector = getPredictor().extract_features(imgpath).reshape(1, -1)
    if (task):
        task.update_state(state='PROGRESS',meta={'current': 60, 'total': 100, 'status': "Predicting using SVR predictor"})
    predicted = clf.predict(feature_vector)
    return predicted




