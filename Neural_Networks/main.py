import matplotlib.pyplot as plt
import nnfs
import numpy as np
from nnfs.datasets import spiral_data

from classes import Layer_Danse, Activation_ReLu, Activation_Softmax, Loss_Crossentropy

nnfs.init()

LOWEST_L = 99999
REPS = 100000
MULTIPLIER = 0.07
prediction = 0
X,y = spiral_data(100,3)

dense1 = Layer_Danse(2,3)
dense2 = Layer_Danse(3,3)
activation1 = Activation_ReLu()
activation2 = Activation_Softmax()

loss_fun = Loss_Crossentropy()
best_d1_weights = dense1.weights.copy()
best_d2_weights = dense2.weights.copy()
best_d1_biases = dense1.biases.copy()
best_d2_biases = dense2.biases.copy()

for i in range(REPS):
    dense1.weights += np.random.randn(2,3) * MULTIPLIER
    dense2.weights += np.random.randn(3,3) * MULTIPLIER
    dense1.biases += np.random.randn(1,3) * MULTIPLIER
    dense2.biases += np.random.randn(1,3) * MULTIPLIER

    dense1.forward(X)
    activation1.forward(dense1.output)
    dense2.forward(activation1.output)
    activation2.forward(dense2.output)

    loss = loss_fun.calculate(activation2.output, y)

    prediction = np.argmax(activation2.output, axis=1)
    accuracy = np.mean(prediction == y)

    if loss < LOWEST_L:
        print( "Set new lowest loss, iteration:"+
               str(i) +", loss:" + str(loss) +", accuracy:" + str(accuracy))
        best_d1_weights = dense1.weights.copy()
        best_d2_weights = dense2.weights.copy()
        best_d1_biases = dense1.biases.copy()
        best_d2_biases = dense2.biases.copy()
        LOWEST_L = loss
    else:
        dense1.weights = best_d1_weights.copy()
        dense2.weights = best_d2_weights.copy()
        dense1.biases = best_d1_biases.copy()
        dense2.biases = best_d2_biases.copy()


plt.scatter(X[:, 0], X[:, 1], c=prediction,cmap="brg")
plt.show()