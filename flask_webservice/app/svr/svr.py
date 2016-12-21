# set up Python environment: numpy for numerical routines...
import numpy as np
import pickle
from faster_rcnn_feature_extractor import Predictor

predictorPref = None
predictorFirst = None


def getPredictor():
    global predictorPref

    if predictorPref is None:
        predictorPref = Predictor()

    return predictorPref


clf_pref = pickle.load(open("app/svr/svr_test_pref_26.10.sk", 'rb'))
clf_first = pickle.load(open("app/svr/svr_test_first_after_gs_28.08.sk", 'rb'))


def predict(imgpath, task=None, svr_type="pref"):
    if (task):
        task.update_state(state='PROGRESS',meta={'current': 10 , 'total': 100, 'status': "Getting neural network feature extractor"})
    feature_vector = getPredictor().extract_features(imgpath).reshape(1, -1)
    if (task):
        task.update_state(state='PROGRESS',meta={'current': 60, 'total': 100, 'status': "Predicting using SVR predictor"})
    if (svr_type == "pref"):
        predicted = clf_pref.predict(feature_vector)
    elif (svr_type == "first"):
        predicted = clf_first.predict(feature_vector)
    return predicted




