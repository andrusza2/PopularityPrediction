# set up Python environment: numpy for numerical routines...
import numpy as np
import scipy.stats as stat
import pickle
from sklearn import svm
from sklearn.cross_validation import KFold, train_test_split

import sys


with open("fb_first_pref2.txt") as views:
    views_list = [float(i.split()[2]) for i in views.read().splitlines()]


views2 = np.array(views_list)


print "Loading outputs..."
outputs = pickle.load(open('outputs_fc_dump_ave_03.08.pickle', 'rb'))

# print outputs

outputs = np.array(outputs)
# outputs_pref = np.array([i[1000:] for i in outputs])

print outputs.shape
# print outputs_pref.shape

# outputs2 = np.array(outputs)


X_train, X_test, y_train, y_test = train_test_split(outputs, views2, test_size=0.2, random_state=42)


X_train.reshape(1,-1)
X_test.reshape(1,-1)

clf = svm.SVR(kernel='rbf', gamma=0.001, C=10, verbose=3)

print "Fitting..."
sys.stdout.flush()

clf.fit(X_train, y_train)

pickle.dump(clf, open('svr_test_ave_after_gs_05.08.sk', 'wb'))

predicted = clf.predict(X_test)

sp = stat.spearmanr(predicted, y_test)

print sp[0]
print sp[1]
sys.stdout.flush()

score = clf.score(X_test, y_test)

print "Score: ", score
sys.stdout.flush()




print "Starting KFold..."

### KFold for first:
kf = KFold(outputs.shape[0], n_folds=5, shuffle=True, random_state=42)

for train, test in kf:
    print "Next iterration..."
    sys.stdout.flush()

    X_train, X_test, y_train, y_test = outputs[train], outputs[test], views2[train], views2[test]

    # X_train.reshape(1, -1)
    # X_test.reshape(1, -1)

    clf = svm.SVR(kernel='rbf', gamma=0.001, C=10, verbose=3)

    print "Fitting..."
    sys.stdout.flush()

    clf.fit(X_train, y_train)

    # pickle.dump(clf, open('svr_test_ext_19.06.sk', 'wb'))

    predicted = clf.predict(X_test)

    sp = stat.spearmanr(predicted, y_test)

    print sp[0]
    print sp[1]
    sys.stdout.flush()

    score = clf.score(X_test, y_test)

    print "Score: ", score
    sys.stdout.flush()


# ### KFold for pref:
# kf = KFold(outputs_pref.shape[0], n_folds=5)

# for train, test in kf:
#     print "Next iterration..."
#     sys.stdout.flush()

#     X_train, X_test, y_train, y_test = outputs_pref[train], outputs_pref[test], views2[train], views2[test]

#     # X_train.reshape(1, -1)
#     # X_test.reshape(1, -1)

#     clf = svm.SVR(verbose=3)

#     print "Fitting..."
#     sys.stdout.flush()

#     clf.fit(X_train, y_train)

#     # pickle.dump(clf, open('svr_test_ext_19.06.sk', 'wb'))

#     predicted = clf.predict(X_test)

#     sp = stat.spearmanr(predicted, y_test)

#     print sp[0]
#     print sp[1]
#     sys.stdout.flush()

#     score = clf.score(X_test, y_test)

#     print "Score: ", score
#     sys.stdout.flush()


# X_train, X_test, y_train, y_test = train_test_split(outputs2, views2, test_size=0.2, random_state=42)


# X_train.reshape(1,-1)
# X_test.reshape(1,-1)


# ### SPEARMAN CORRELATION for every feature ###
# spearman_corr = []
# p_value = []
#
# for i in range (0, 999):
#     x = [o[i] for o in outputs2]
#     # print x
#     # print len(x)
#     # print len(views2)
#     sp = stat.spearmanr(x,views2)
#     spearman_corr.append(sp[0])
#     p_value.append(sp[1])
#
# spearman_corr.sort(reverse=True)
#
# print spearman_corr
# sys.stdout.flush()

