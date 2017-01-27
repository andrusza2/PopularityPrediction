"""
Module with celery task for popularity prediction.
"""

from . import celery
from . import Config

import os

import pickle
from resnet.feature_extractor import FeatureExtractor

import ffmpy


def extract_first_frame(video_filename):
    """

    :param video_filename:
    :type video_filename:
    :return:
    :rtype:
    """
    video_filename = os.path.join(Config.UPLOAD_FOLDER, video_filename)

    first_scene_filename = video_filename + '_first.jpg'
    ff = ffmpy.FFmpeg(inputs={video_filename: None},
                      outputs={first_scene_filename: '-vf "select=gte(n\,25)" -y -vframes 1'})
    ff.run()
    return first_scene_filename.split("/")[-1]



def get_quantile_score(prediction_result, classifier="first"):
    """
    Get final score using quantiles (computed before).
    :param prediction_result: Regression result from SVR
    :type prediction_result: float
    :param classifier: Which classifier is in use (possible: "first" or "pref")
    :type classifier: str
    :return: Prediction score in 0.1-10.0 scale
    :rtype: float
    """

    if classifier == "first":
        quantiles = Config.SVR_FIRST_QUANTILES
    elif classifier == "pref":
        quantiles = Config.SVR_PREF_QUANTILES
    else:
        raise Exception("Unsupported classifier type")

    if len(quantiles) != 99:
        raise Exception("Wrong quantiles. Check config file")

    for (i, quantile) in enumerate(quantiles):
        if prediction_result < quantile:
            return (i+1)/10.0

    return 10.0


class PopularityPredictionTask(celery.Task):
    """
    Custom Celery task.
    Containing neural network for feature extraction and SVR's models for prediction.
    """

    _feature_extractor = None

    clf_pref = pickle.load(open(Config.SVR_PREF_PATH, 'rb'))
    clf_first = pickle.load(open(Config.SVR_FIRST_PATH, 'rb'))

    @property
    def feature_extractor(self):
        """
        Feature extractor property.
        Lazy neural network initialization (in order to get one Caffe Network object per celery-worker).
        :return: Feature Extractor class object
        :rtype: FeatureExtractor
        """
        if self._feature_extractor is None:
            self._feature_extractor = FeatureExtractor()
        return self._feature_extractor


@celery.task(base=PopularityPredictionTask, bind=True)
def prediction_task(self, imgpath):
    """
    Task for thumbnail-based popularity prediction
    :param self: Celery task
    :type self: PopularityPredictionTask
    :param imgpath: Path to image file
    :type imgpath: str
    :return: Json with task status and prediction results
    """

    self.update_state(state='PROGRESS',
                          meta={'current': 10, 'total': 100, 'status': "Getting neural network feature extractor"})

    # extract feature vector
    feature_vector = self.feature_extractor.extract_features(imgpath).reshape(1, -1)

    self.update_state(state='PROGRESS',
                          meta={'current': 40, 'total': 100, 'status': "Predicting using first thumbnail SVR predictor"})

    # predict using first-thumbnail predictor
    predicted_first = self.clf_first.predict(feature_vector, )
    score_first = get_quantile_score(predicted_first[0], classifier="first")

    self.update_state(state='PROGRESS',
                      meta={'current': 60, 'total': 100, 'status': "Predicting using preferred thumbnail SVR predictor"})

    # predict using preferred-thumbnail predictor
    predicted_pref = self.clf_pref.predict(feature_vector)

    self.update_state(state='PROGRESS',
                      meta={'current': 80, 'total': 100,
                            'status': "Getting quantile score"})

    score_pref = get_quantile_score(predicted_pref[0], classifier="pref")

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': {'first': score_first, 'pref': score_pref}}

