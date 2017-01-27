"""
Module with neural network feature extractor.
"""

# set up Python environment: numpy for numerical routines, and matplotlib for plotting
import numpy as np
from .. import Config


# # The caffe module needs to be on the Python path;
# #  we'll add it here explicitly.
# import sys
# caffe_root = '/opt/caffe/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
# sys.path.insert(0, caffe_root + 'python')

import caffe
# If you get "No module named _caffe", either you have not built pycaffe or you have the wrong path.


class FeatureExtractor:
    """
    Neural network feature extractor.
    """

    def __init__(self):
        model_def = Config.RESNET_PROTOTXT_PATH
        model_weights = Config.RESNET_CAFFEMODEL_PATH

        # load the mean ImageNet image (as distributed with Caffe) for subtraction
        mu = np.load(Config.MEAN_IMAGE_PATH)
        mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values


        self.net = caffe.Net(model_def,      # defines the structure of the model
                        model_weights,  # contains the trained weights
                        caffe.TEST)     # use test mode (e.g., don't perform dropout)

        # create transformer for the input called 'data'
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})

        self.transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost dimension
        self.transformer.set_mean('data', mu)  # subtract the dataset-mean value in each channel
        self.transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
        self.transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

        # set the size of the input
        self.net.blobs['data'].reshape(2,        # batch size
                                  3,         # 3-channel (BGR) images
                                  224, 224)  # image size is 224x224

        if (Config.CAFFE_MODE == "gpu"):
            caffe.set_device(0)  # if we have multiple GPUs, pick the first one
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()

    def extract_features(self, img_path):
        """
        Method for extracting feature vector from image, using deep neural network.
        :param img_path: Path to image file
        :type img_path: str
        :return: Feature vector of length 1000 containing
        :rtype: numpy.ndarray
        """

        # load and transform image
        image = caffe.io.load_image(img_path)
        transformed_image = self.transformer.preprocess('data', image)

        # copy the image data into the memory allocated for the net
        self.net.blobs['data'].data[...] = transformed_image

        # perform classification
        output = self.net.forward()

        # copy activations of the last fully-connected layer
        data_fc = self.net.blobs['fc1000'].data[0].copy()

        return data_fc

