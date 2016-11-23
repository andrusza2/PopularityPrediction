# set up Python environment: numpy for numerical routines, and matplotlib for plotting
import numpy as np
import scipy.stats as stat
import pickle


# The caffe module needs to be on the Python path;
#  we'll add it here explicitly.
import sys
caffe_root = '/opt/caffe/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
sys.path.insert(0, caffe_root + 'python')

import caffe
# If you get "No module named _caffe", either you have not built pycaffe or you have the wrong path.

import os


class Predictor:

    net = None
    transformer = None

    def __init__(self):

        resnet_root = "/media/andrusza2/Nowy/Workspace/deep-residual-networks/"
        if os.path.isfile(resnet_root + 'ResNet-152-model.caffemodel'):
            print 'ResNet found.'

        model_def = resnet_root + 'prototxt/ResNet-152-deploy.prototxt'
        model_weights = resnet_root + 'ResNet-152-model.caffemodel'

        # load the mean ImageNet image (as distributed with Caffe) for subtraction
        mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
        mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
        print 'mean-subtracted values:', zip('BGR', mu)

        self.net = caffe.Net(model_def,      # defines the structure of the model
                        model_weights,  # contains the trained weights
                        caffe.TEST)     # use test mode (e.g., don't perform dropout)

        # create transformer for the input called 'data'
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})

        self.transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
        self.transformer.set_mean('data', mu)  # subtract the dataset-mean value in each channel
        self.transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
        self.transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

        # set the size of the input (we can skip this if we're happy
        #  with the default; we can also change it later, e.g., for different batch sizes)
        self.net.blobs['data'].reshape(2,        # batch size
                                  3,         # 3-channel (BGR) images
                                  224, 224)  # image size is 227x227

        caffe.set_device(0)  # if we have multiple GPUs, pick the first one
        caffe.set_mode_gpu()


    def extract_features(self, img_path):
        image = caffe.io.load_image(img_path)
        transformed_image = self.transformer.preprocess('data', image)

        # copy the image data into the memory allocated for the net
        self.net.blobs['data'].data[...] = transformed_image

        ### perform classification
        output = self.net.forward()
        data_fc = self.net.blobs['fc1000'].data[0].copy()

        return data_fc

