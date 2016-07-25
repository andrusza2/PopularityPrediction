# set up Python environment: numpy for numerical routines...
import numpy as np
import scipy.stats as stat
import pickle
from sklearn import svm
from sklearn.cross_validation import KFold, train_test_split
from sklearn.grid_search import GridSearchCV

import sys
import time


with open("fb_first_pref2.txt") as views:
    views_list = [float(i.split()[2]) for i in views.read().splitlines()]


views2 = np.array(views_list)


print "Loading outputs..."
outputs = pickle.load(open('outputs_fc_dump_ext_11.07.pickle', 'rb'))

outputs2 = np.array(outputs)


X_train, X_test, y_train, y_test = train_test_split(outputs2, views2, test_size=0.2, random_state=42)

X_train.reshape(1,-1)
X_test.reshape(1,-1)

# svr = GridSearchCV(svm.SVR(kernel='rbf', gamma=0.001, verbose=3), cv=3,
#                    param_grid={"C": [1e0, 1e1, 1e2],
#                                "gamma": np.logspace(-3, 0, 4)})

print "Loading SVR GridSearch..."

svr = pickle.load(open('svr_grid_test_ext_18.07.sk', 'rb'))

# t0 = time.time()

# print "Fitting..."
# sys.stdout.flush()
# svr.fit(outputs2, views2)

# svr_fit = time.time() - t0

# print("SVR complexity and bandwidth selected and model fitted in %.3f s"
#       % svr_fit)

# sys.stdout.flush()

# pickle.dump(svr, open('svr_grid_test_ext_18.07.sk', 'wb'))

# pickle.dump(svr.best_estimator_, open('svr_grid_test_best_ext_18.07.sk', 'wb'))

print svr.grid_scores_
sys.stdout.flush()

clf = svr.best_estimator_


predicted = clf.predict(X_test)

sp = stat.spearmanr(predicted, y_test)

print sp[0]
print sp[1]
sys.stdout.flush()

score = clf.score(X_test, y_test)

print "Score: ", score
sys.stdout.flush()
