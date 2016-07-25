# set up Python environment: numpy for numerical routines, and matplotlib for plotting
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import pickle

# set display defaults
plt.rcParams['figure.figsize'] = (10, 10)        # large images
plt.rcParams['image.interpolation'] = 'nearest'  # don't interpolate: show square pixels
plt.rcParams['image.cmap'] = 'gray'  # use grayscale output rather than a (potentially misleading) color heatmap

# The caffe module needs to be on the Python path;
#  we'll add it here explicitly.
import sys
caffe_root = '/opt/caffe/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
sys.path.insert(0, caffe_root + 'python')

import caffe
# If you get "No module named _caffe", either you have not built pycaffe or you have the wrong path.

import os

resnet_root = "/opt/deep-residual-networks/"
if os.path.isfile(resnet_root + 'models/ResNet-152-model.caffemodel'):
    print 'ResNet found.'

with open("fb_first_pref2.txt") as imglist:
    img_list = imglist.read().splitlines()


model_def = resnet_root + 'prototxt/ResNet-152-deploy.prototxt'
model_weights = resnet_root + 'models/ResNet-152-model.caffemodel'

net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

# load the mean ImageNet image (as distributed with Caffe) for subtraction
mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
print 'mean-subtracted values:', zip('BGR', mu)

# create transformer for the input called 'data'
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR

# set the size of the input (we can skip this if we're happy
#  with the default; we can also change it later, e.g., for different batch sizes)
net.blobs['data'].reshape(2,        # batch size
                          3,         # 3-channel (BGR) images
                          224, 224)  # image size is 227x227

caffe.set_device(0)  # if we have multiple GPUs, pick the first one
caffe.set_mode_gpu()

outputs_extend = []

outputs_average = []


for i, img in enumerate(img_list):
        image = caffe.io.load_image(img.split()[0])
        transformed_image = transformer.preprocess('data', image)

        # copy the image data into the memory allocated for the net
        net.blobs['data'].data[...] = transformed_image

        ### perform classification
        output = net.forward()
        data_fc = net.blobs['fc1000'].data[0].copy()

        image2 = caffe.io.load_image(img.split()[0])
        transformed_image = transformer.preprocess('data', image)

        # copy the image data into the memory allocated for the net
        net.blobs['data'].data[...] = transformed_image

        ### perform classification
        output2 = net.forward()
        data_fc2 = net.blobs['fc1000'].data[0].copy()

        print i, '...'
        sys.stdout.flush()

        outputs_extend.append(np.append(data_fc, data_fc2))
        outputs_average.append(np.mean(np.array([data_fc, data_fc2]), axis=0))

        # print outputs_extend[0].shape
        # print outputs_average[0].shape

        # print output['fc1000'][0]

        # output_prob = np.array(output['prob'][0])  # the output probability vector for the  image

        ### print output vector
        # print python array
        # print output_prob

        # # prin comma-separated style
        # print ','.join(map(str, output_prob))

        if (i%10000 == 0):
            pickle.dump(outputs_extend, open('outputs_fc_dump_ext_11.07_' + repr(i) + '.pickle', 'wb'))
            pickle.dump(outputs_average, open('outputs_fc_dump_ave_11.07_' + repr(i) + '.pickle', 'wb'))

    # print outputs

pickle.dump(outputs_extend, open('outputs_fc_dump_ext_11.07.pickle', 'wb'))
pickle.dump(outputs_average, open('outputs_fc_dump_ave_11.07.pickle', 'wb'))

# for img in img_list:
#
#     image = caffe.io.load_image(img.split()[0])
#     transformed_image = transformer.preprocess('data', image)
#
#     # copy the image data into the memory allocated for the net
#     net.blobs['data'].data[...] = transformed_image
#
#     ### perform classification
#     output = net.forward()
#
#     output_prob = np.array(output['prob'][0])  # the output probability vector for the first image in the batch
#
#     outputs.append(output_prob)
#
#     # print output_prob
#     #
#     print 'predicted class is:', output_prob.argmax()
#     #
#     # # load ImageNet labels
#     # labels_file = caffe_root + 'data/ilsvrc12/synset_words.txt'
#     #
#     # labels = np.loadtxt(labels_file, str, delimiter='\t')
#     #
#     # print 'output label:', labels[output_prob.argmax()]
#     #
#     # # sort top five predictions from softmax output
#     # top_inds = output_prob.argsort()[::-1][:5]  # reverse sort and take five largest items
#     #
#     # # print top_inds
#     #
#     # print 'probabilities and labels:'
#     # print zip(output_prob[top_inds], labels[top_inds])
#
# outputs2 = np.array(outputs)
#
# spearman_corr = []
# p_value = []
#
# for i in range (0, 999):
#     x = [o[i] for o in outputs2]
#     print x
#     print len(x)
#     print len(views_list)
#     sp = stat.spearmanr(x,views_list)
#     spearman_corr.append(sp[0])
#     p_value.append(sp[1])
#
# print spearman_corr
# print p_value





# caffe.set_device(0)  # if we have multiple GPUs, pick the first one
# caffe.set_mode_gpu()
# net.forward()  # run once before timing to set up memory

# # for each layer, show the output shape
# for layer_name, blob in net.blobs.iteritems():
#     print layer_name + '\t' + str(blob.data.shape)