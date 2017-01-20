from . import celery
from . import Config

import pickle
from resnet.feature_extractor import FeatureExtractor


def get_quantile_score(prediction_result, classifier="first"):

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

    _feature_extractor = None

    clf_pref = pickle.load(open(Config.SVR_PREF_PATH, 'rb'))
    clf_first = pickle.load(open(Config.SVR_FIRST_PATH, 'rb'))

    @property
    def feature_extractor(self):
        if self._feature_extractor is None:
            self._feature_extractor = FeatureExtractor()
        return self._feature_extractor


@celery.task(base=PopularityPredictionTask, bind=True)
def long_task(self, imgpath):

    self.update_state(state='PROGRESS',
                          meta={'current': 10, 'total': 100, 'status': "Getting neural network feature extractor"})

    feature_vector = self.feature_extractor.extract_features(imgpath).reshape(1, -1)

    self.update_state(state='PROGRESS',
                          meta={'current': 40, 'total': 100, 'status': "Predicting using first thumbnail SVR predictor"})

    predicted_first = self.clf_first.predict(feature_vector, )
    score_first = get_quantile_score(predicted_first[0], classifier="first")

    self.update_state(state='PROGRESS',
                      meta={'current': 60, 'total': 100, 'status': "Predicting using preferred thumbnail SVR predictor"})

    predicted_pref = self.clf_pref.predict(feature_vector)
    score_pref = get_quantile_score(predicted_pref[0], classifier="pref")

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': {'first': score_first, 'pref': score_pref}}

