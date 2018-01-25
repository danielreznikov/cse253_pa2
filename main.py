import numpy as np
import matplotlib.pyplot as plt
import math
from pprint import pprint
import utilities
from multi_layer_preceptron import *

def main():
    data = utilities.read_data(train_size=100, test_size=1)

    num_epochs = 25

    mlp = MLP(input_units=785, hidden_layers=1, hidden_units=64, output_units=10)

    weights, accuracies = mlp.train(data, max_epochs=num_epochs, learning_rate_init=0.001, lam=0, reg=None, annealing=1000)

    x = np.arange(num_epochs)

    plt.plot(x, accuracies['train_acc'])
    plt.xlabel('epoch')
    plt.ylabel('Percent Accuracy')
    # plt.legend(['train_acc', 'valid_acc', 'test_acc'], loc='upper right')
    plt.show()


main()