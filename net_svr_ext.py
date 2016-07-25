# set up Python environment: numpy for numerical routines, and matplotlib for plotting
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import pickle
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeRegressor

import sys


# with open("img_pref_fb.txt") as imglist:
#     img_list = imglist.read().splitlines()

with open("fb_first_pref2.txt") as views:
    views_list = [float(i.split()[2]) for i in views.read().splitlines()]

# print views_list

views2 = np.array(views_list)
# print normailized_views.shape


print "Loading outputs..."
outputs = pickle.load(open('outputs_fc_dump_ext_11.07.pickle', 'rb'))

print outputs


outputs2 = np.array(outputs)

# views2 = np.log10(views_list)

# views2 = np.array(views_list).astype(float)


X_train, X_test, y_train, y_test = train_test_split(outputs2, views2, test_size=0.2, random_state=42)


X_train.reshape(1,-1)
X_test.reshape(1,-1)

# clf = svm.SVR(verbose=3)

# print "Fitting..."
# sys.stdout.flush()

# clf.fit(X_train, y_train)

# pickle.dump(clf, open('svr_test_1_19.06.sk', 'wb'))

print "Loading fitted svr..."
sys.stdout.flush()

clf = pickle.load(open('svr_test_ext_12.07.sk', 'rb'))


# for i, y in enumerate(y_test):
#     result = clf.predict(X_test[i])
#     print "predicted: ", result, "Acc: ", y

predicted = clf.predict(X_test)

print y_test
print predicted
sys.stdout.flush()

sp = stat.spearmanr(predicted, y_test)

print sp[0]
print sp[1]
sys.stdout.flush()


score = clf.score(X_test, y_test)

print "Score: ", score
sys.stdout.flush()


# clf = DecisionTreeRegressor()
# clf = svm.SVR(degree=3)
#
# print "Fitting..."
# clf.fit(X_train, y_train)
#
# pickle.dump(clf, open('dtr_test_7_fc_pick.sk', 'wb'))
#
#
# for i, y in enumerate(y_test):
#     result = clf.predict(X_test[i])
#     print "predicted: ", result, "Acc: ", y
#
# score = clf.score(X_test, y_test)
#
# print "Score: ", score

# print outputs2

spearman_corr = []
p_value = []

for i in range (0, 999):
    x = [o[i] for o in outputs2]
    # print x
    # print len(x)
    # print len(views2)
    sp = stat.spearmanr(x,views2)
    spearman_corr.append(sp[0])
    p_value.append(sp[1])

spearman_corr.sort(reverse=True)

# np_spearman = np.array(spearman_corr)
#
# print np_spearman.argsort()[:10][::1]
print spearman_corr
sys.stdout.flush()

# print p_value

# print spearman_corr[29]
# print spearman_corr[35]
# print spearman_corr[688]
# print spearman_corr[653]
# print spearman_corr[270]
#
#
#
# print spearman_corr[77]


# caffe.set_device(0)  # if we have multiple GPUs, pick the first one
# caffe.set_mode_gpu()
# net.forward()  # run once before timing to set up memory

# # for each layer, show the output shape
# for layer_name, blob in net.blobs.iteritems():
#     print layer_name + '\t' + str(blob.data.shape)
