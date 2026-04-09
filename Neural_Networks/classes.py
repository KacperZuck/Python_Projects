


import sys

import nnfs
import numpy as np
import matplotlib.pyplot as plt
import nnfs
from numpy import dtype

# np.random.seed(0)
# nnfs.init()

def create_data(points, classes):
    X = np.zeros((points*classes,2))
    y = np.zeros(points*classes,dtype='uint8')
    for class_number in range(classes):
        ix = range(points*class_number, points*(class_number+1))
        r = np.linspace(0.0, 1, points)
        t = np.linspace(class_number*4, (class_number+1)*4, points) + np.random.randn(points)*0.2
        X[ix] = np.c_[r*np.sin(t*2.5),r*np.cos(t*2.5)]
        y[ix] = class_number
    return X,y

# INPUT -- 3 data samples
# X = [[ 1, 2, 3, 2.5],
#      [ 2.0, 5.0, -1.0, 2.0],
#      [ -1.5, 2.7, 3.3, -0.8]]

class Layer_Danse:
    def __init__(self, n_input, n_neurons):
        self.weights = 0.1 * np.random.randn(n_input,n_neurons) # size imput x nuber of neurons
        self.biases = np.zeros((1, n_neurons)) # 1 parametr to shape !!!
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases

class Activation_ReLu:
    def forward(self, inputs):
        self.output = np.maximum(0, inputs)

class Activation_Softmax:
    def forward(self, inputs):
        exp_val = np.exp(inputs - np.max(inputs, axis=1, keepdims=True))
        self.output = exp_val / np.sum(exp_val, axis=1, keepdims=True)

class Loss:
    def calculate(self, output,y):
        sample_losses = self.forward(output,y)
        data_loss = np.mean(sample_losses)
        return data_loss

class Loss_Crossentropy(Loss):
    def forward(self, y_pred, y_true):
        samples = len(y_pred)
        y_pred_clipped = np.clip(y_pred, 1e-7, 1-1e-7)
        if len(y_true.shape) == 1:
            confidences = y_pred_clipped[range(samples), y_true]
        elif len(y_true.shape) == 2:
            confidences = np.sum(y_pred_clipped*y_true, axis=1)
        return -np.log(confidences)

X, y = create_data(100, 3)

# plt.scatter(X[:, 0], X[:, 1])
plt.scatter(X[:, 0], X[:, 1], c=y,cmap="brg")
plt.show()

layer1 = Layer_Danse(2,3) # input 2 bo 2 wymiary (x,y)
layer1.forward(X)

activation = Activation_ReLu()
activation.forward(layer1.output)

layer2 = Layer_Danse(3,3)
layer2.forward(activation.output)

activation2 = Activation_Softmax()
activation2.forward(layer2.output)

loss_fun = Loss_Crossentropy()
loss = loss_fun.calculate(activation2.output, y)

print(loss)
# layer1 = Layer_Danse(4,5)
# layer2 = Layer_Danse(5,2)
#
# layer1.forward(X)
# # print(layer1.output)
# layer2.forward(layer1.output)
# print(layer2.output)












# weights = [
#     [ 0.2, 0.8, -0.5, 1.0],
#     [ 0.5, -0.91, 0.26, -0.5],
#     [ -0.26, -0.27, 0.17, 0.87]]
#
# bias = [ 2, 3, 0.5]
#
# weights2 = [
#     [ 0.1, -0.14, 0.5],
#     [ -0.5, 0.12, -0.33],
#     [ -0.44, 0.73, -0.13]]
#
# bias2 = [ -1,2,-0.5]
#
# layer1_out = np.dot(inputs, np.array(weights).T) + bias
# layer2_out = np.dot(layer1_out, np.array(weights2).T) + bias2
#
# print(layer2_out)