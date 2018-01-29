import numpy as np
import utilities
from matplotlib import pyplot as plt
from time import time
import sys

class MLP(object):
    """This is our neural network object."""

    def __init__(self, input_units, hidden_layers, hidden_units, output_units, hidden_activation='sigmoid', output_activation='softmax'):
        assert(hidden_layers == 1 or hidden_layers ==2)

        self.input_units = input_units
        self.hidden_layers = hidden_layers
        self.hidden_units = hidden_units
        self.output_units = output_units
        self.dims = 785
        self.num_layers = hidden_layers + 1
        self.train_stats = None

        self.losses = {'train_loss': [], 'valid_loss': [], 'test_loss': []}
        self.accuracies = {'train_acc': [],'valid_acc': [],'test_acc': []}

        if hidden_layers == 1:
            self.weights = [
                # Experiment 3E, 4A, 4B
                # np.random.uniform(low=-1.0, high=1.0, size=(self.input_units, self.hidden_units-1)),
                # np.random.uniform(low=-1.0, high=1.0, size=(self.hidden_units, self.output_units))

                np.random.normal(loc=0, scale=1/np.sqrt(self.input_units),  size=(self.input_units, self.hidden_units-1)),
                np.random.normal(loc=0, scale=1/np.sqrt(self.hidden_units), size=(self.hidden_units, self.output_units))
            ]
        elif hidden_layers == 2:
            self.weights = [
                np.random.normal(loc=0, scale=1 / np.sqrt(self.input_units),  size=(self.input_units, self.hidden_units  - 1)),
                np.random.normal(loc=0, scale=1 / np.sqrt(self.hidden_units), size=(self.hidden_units, self.hidden_units - 1)),
                np.random.normal(loc=0, scale=1 / np.sqrt(self.hidden_units), size=(self.hidden_units, self.output_units))
            ]

        self.best_model = [sys.maxsize, self.weights]

        if hidden_activation == 'sigmoid':
            self.hidden_activation = utilities.sigmoid_activation
        elif hidden_activation == 'tanh':
            self.hidden_activation = utilities.tanh_activation
        else:
            raise Exception("ERROR: unsuported activation function," + hidden_activation)

        if output_activation == 'softmax':
            self.output_activation = utilities.softmax_activation
        else:
            raise Exception("ERROR: unsuported activation function," + output_activation)

    def goodstuff(self, data, max_epochs=100, learning_rate_init=0.0001, lam=0, reg=None, annealing=100, batch_size=None, shuffle=False):

        xTrain = np.copy(data['xTrain'])
        yTrain = np.copy(data['yTrain'])
        xTest = np.copy(data['xTest'])
        yTest = np.copy(data['yTest'])

        # train_loss_record = []
        # valid_loss_record = []
        # test_loss_record = []
        weights_record = []

        train_accuracy = []
        # valid_accuracy = []
        # test_accuracy = []

        weights = []
        net_inputs = []
        net_outputs = []
        deltas = []

        np.random.seed(2018)

        # Split data into train and validation
        indices = np.random.randint(0, xTrain.shape[0], xTrain.shape[0] // 10)
        xValid = xTrain[indices]
        yValid = yTrain[indices]
        np.delete(xTrain, indices, axis=0)
        np.delete(yTrain, indices, axis=0)

        datasets = {'train': xTrain, 'valid': xValid, 'test': xTest}

        # Mini-batching
        batches = []
        if shuffle:
            indices = np.random.permutation(xTrain.shape[0])
        else:
            indices = np.arange(xTrain.shape[0])

        if batch_size==None:
            batch_size = xTrain.shape[0]

        for batch_num in range(xTrain.shape[0] // batch_size):
            indxs = indices[batch_num*batch_size:(batch_num+1)*batch_size]
            batches.append((xTrain[indxs], yTrain[indxs]))

        # Initialize weights list indexing into each layer (looks good)
        for layer in range(self.num_layers):
            if layer == 0: # layer0
                weights.append(np.random.normal(loc=0, scale=1, size=(self.dims, self.hidden_units)))
            elif layer < self.num_layers - 1: # hidden layers
                weights.append(np.random.normal(loc=0, scale=1, size=(self.hidden_units, self.hidden_units)))
            else: # last layer
                weights.append(np.random.normal(loc=0, scale=1, size=(self.hidden_units, self.output_units)))

        # Iterate over epochs
        for epoch in range(max_epochs):
            for train, labels in batches:
                # learning_rate = learning_rate_init / (1 + epoch / annealing)
                learning_rate = learning_rate_init

                # Forward propogation to get model weights
                for layer in range(self.num_layers):
                    if layer == 0:
                        net_inputs.append(np.dot(train, weights[layer]))
                        net_outputs.append(self.hidden_activation(net_inputs[layer]))
                    elif layer < self.num_layers - 1:
                        net_inputs.append(np.dot(net_outputs[layer-1], weights[layer]))
                        net_outputs.append(self.hidden_activation(net_inputs[-1]))
                    else:
                        net_inputs.append(np.dot(net_outputs[layer-1], weights[layer]))
                        net_outputs.append(self.output_activation(net_inputs[-1]))

                # Backprop of partial gradients via deltas
                for layer in range(self.num_layers-1, -1, -1):
                    if layer == self.num_layers-1:
                        deltas.append(labels - net_outputs[-1])
                    else:
                        delta = net_outputs[layer]*(1 - net_outputs[layer]) * np.dot(deltas[-1], weights[layer+1].T)
                        deltas.append(delta)

                deltas = list(reversed(deltas))

                # Update weights via gradient descent
                for layer in range(self.num_layers):
                    if layer == 0:
                        grad = np.dot(train.T, deltas[layer])
                        weights[layer] += learning_rate * np.dot(train.T, deltas[layer])
                    else:
                        grad = np.dot(net_outputs[layer-1].T, deltas[layer])
                        weights[layer] += learning_rate * np.dot(net_outputs[layer-1].T, deltas[layer])

                # Regularization
                if reg == 'L2':
                    weights -= lam * 2 * weights
                elif reg == 'L1':
                    weights -= lam * np.sign(weights)

            weights_record.append(weights)

            # Get Model Predictions
            # predictions =  np.argmax(net_outputs[-1], axis=1) #TODO commented out hard model predictions

            # for key, dataset in datasets:
            #     # TODO update to predict for valid/test datasets
            #     predictions[key] = np.argmax(net_outputs[-1], axis=1)

            # Compute Accuracy

            # print(np.argmax(yTrain, axis=1)[:10], np.argmax(net_outputs[-1], axis=1)[:10])
            # sys.exit()

            train_accuracy.append(utilities.accuracy(yTrain, net_outputs[-1])) #TODO Changed predictions to netout bc 1hot
            # valid_accuracy.append(accuracy_softmax(yValid, predictions_valid))
            # test_accuracy.append(accuracy_softmax(yTest, predictions_test))

            # Compute Loss
            # train_loss_record.append(cross_entropy_loss_softmax(yTrain, predictions_train))
            # valid_loss_record.append(cross_entropy_loss_softmax(yValid, predictions_valid))
            # test_loss_record.append(cross_entropy_loss_softmax(yTest, predictions_test))

        # Format output
        # losses = {'train_loss': train_loss_record,
        #           'valid_loss': valid_loss_record,
        #           'test_loss': test_loss_record,
        #           }

        accuracies = {'train_acc': train_accuracy,
                      # 'valid_acc': valid_accuracy,
                      # 'test_acc': test_accuracy
                      }

        # return weights, losses, weights_record, accuracies
        return weights, accuracies

    def train_hidden1(self, max_epochs=100, learning_rate_init=0.0001, annealing=100, batch_size=None, shuffle=False, gradient_checking=False, momentum=False):
        assert (self.hidden_layers == 1)

        # Start a Timer for Training
        strt = time()
        print("Training...")

        # # Mini-batching
        # batches = []
        # num_samples = self.xTrain.shape[0]
        #
        # if shuffle:
        #     indices = np.random.permutation(num_samples)
        # else:
        #     indices = np.arange(num_samples)
        #
        # if batch_size == None:
        #     batch_size = num_samples
        #
        # for batch_num in range(num_samples // batch_size):
        #     indxs = indices[batch_num * batch_size:(batch_num + 1) * batch_size]
        #     batches.append((self.xTrain[indxs], self.yTrain[indxs]))

        W_hidden1 = self.weights[0]
        W_output = self.weights[1]

        momentum1 = 0
        momentum2 = 0

        # Iterate
        for epoch in range(max_epochs):
            # Decay Learning Rate
            if not momentum:
                alpha = learning_rate_init / (1 + epoch / annealing)
            else:
                alpha = learning_rate_init / (1 + epoch / annealing)

            # Mini-batching
            batches = []
            num_samples = self.xTrain.shape[0]

            if shuffle:
                indices = np.random.permutation(num_samples)
            else:
                indices = np.arange(num_samples)

            if batch_size == None:
                batch_size = num_samples

            for batch_num in range(num_samples // batch_size):
                indxs = indices[batch_num * batch_size:(batch_num + 1) * batch_size]
                batches.append((self.xTrain[indxs], self.yTrain[indxs]))

            # Iterate Over Mini-Batches
            for x_batch, t_batch in batches:
                # Forward Prop
                net_input_h1 = np.dot(x_batch, W_hidden1)
                hidden_layer_out1 = self.hidden_activation(net_input_h1)
                hidden_layer_out1 = np.insert(hidden_layer_out1, 0, 1, axis=1)

                # Output Layer
                net_input_o = np.dot(hidden_layer_out1, W_output)
                y = utilities.softmax_activation(net_input_o)

                # Backprop (deltas)
                delta_output = (t_batch - y)
                if self.hidden_activation == utilities.sigmoid_activation:
                    delta_hidden1 = utilities.sigmoid_activation(net_input_h1) * (1 - utilities.sigmoid_activation(net_input_h1)) * np.dot(delta_output, W_output[1:,:].T)
                elif self.hidden_activation == utilities.tanh_activation:
                    delta_hidden1 = (2/3) * (1.7159 - 1.0/1.7159*np.power(utilities.tanh_activation(net_input_h1), 2)) * np.dot(delta_output, W_output[1:,:].T)
                    # delta_hidden1 = ((-2/3) * (1.7159) * (1 - np.power(np.tanh((2/3) * net_input_h1), 2)) + 0.0)*  np.dot(delta_output, W_output[1:,:].T)

                else:
                    raise Exception("ERROR: Not supported hidden activation function!")

                if gradient_checking == True:
                    # Tune which weight and which layer for gradient checking here!
                    weight_indices = (0, 3)
                    layer_tag = 'output'

                    if layer_tag == 'output':
                        numerical_grad = self.get_numerical_gradient(x_batch, t_batch, layer_tag, weight_indices)
                        backprop_grad = - np.dot(hidden_layer_out1.T, delta_output)[weight_indices]

                        print('Numerical Gradient:', numerical_grad)
                        print('Backprop Gradient:', backprop_grad)
                        print('Difference between Gradient:', numerical_grad - backprop_grad)

                    elif layer_tag == 'hidden':
                        numerical_grad = self.get_numerical_gradient(x_batch, t_batch, layer_tag, weight_indices)
                        backprop_grad = - np.dot(x_batch.T, delta_hidden1)[weight_indices]

                        print('Numerical Gradient:', numerical_grad)
                        print('Backprop Gradient:', backprop_grad)
                        print('Difference between Gradient:', numerical_grad - backprop_grad)

                    else:
                        print('Invalid Tag')
                    sys.exit()

                # Gradient Descent
                if momentum == True:

                    current_grad1 = alpha * np.dot(hidden_layer_out1.T, delta_output)
                    current_grad2 = alpha * np.dot(x_batch.T, delta_hidden1)

                    W_output = W_output + current_grad1 + (0.9 * momentum1)
                    W_hidden1 = W_hidden1 + current_grad2 + (0.9 * momentum2)

                    momentum1 = current_grad1
                    momentum2 = current_grad2

                else:
                    W_output = W_output + alpha * np.dot(hidden_layer_out1.T, delta_output)
                    W_hidden1 = W_hidden1 + alpha * np.dot(x_batch.T, delta_hidden1)

                # Store the Model
                self.weights[0] = W_hidden1
                self.weights[1] = W_output

            # Get model predictions
            predictions_train = self.get_model_predictions(self.xTrain)
            predictions_valid = self.get_model_predictions(self.xValid)
            predictions_test = self.get_model_predictions(self.xTest)

            # Compute accuracies over epochs
            self.accuracies['train_acc'].append(utilities.accuracy(self.yTrain, predictions_train))
            self.accuracies['valid_acc'].append(utilities.accuracy(self.yValid, predictions_valid))
            self.accuracies['test_acc'].append(utilities.accuracy(self.yTest, predictions_test))

            # Code Profiling
            if not self.train_stats and self.accuracies['valid_acc'][-1] >= 0.97:
                self.train_stats = (time() - strt, epoch)

            # Cross-Entropy Loss over epochs
            self.losses['train_loss'].append(utilities.cross_entropy_loss(self.yTrain, predictions_train))
            self.losses['valid_loss'].append(utilities.cross_entropy_loss(self.yValid, predictions_valid))
            self.losses['test_loss'].append(utilities.cross_entropy_loss(self.yTest, predictions_test))

            # Update best model so far
            if self.losses['valid_loss'][-1] < self.best_model[0]:
                self.best_model[0] = self.losses['valid_loss'][-1]
                self.best_model[1] = self.weights

            # Early Stopping
            if epoch > 4 and utilities.early_stopping(self.losses['valid_loss']):
                print("\tEarly Stopping at epoch =", epoch)
                # break
            elif epoch > 2 and np.abs(self.losses['valid_loss'][-1] - self.losses['valid_loss'][-2]) < 0.00001:
                print("\tEarly Stopping, error below epsilon.", self.losses['valid_loss'][-1])
                # break

            # Debug statements
            if epoch % 10 == 0:
                print("\nEpoch:", epoch)
                print("\tAccuracy:", self.accuracies['train_acc'][-1])
                print("\tLoss:", self.losses['train_loss'][-1])

        if not self.train_stats:
            self.train_stats = (time() - strt, epoch)

        print('\n\nTraining Done! Took', round(time() - strt, 3), " secs.")
        print('Final Training Accuracy: ', self.accuracies['train_acc'][-1], " in ", epoch, " epochs.")

        return 1

    def train_hidden2(self, max_epochs=100, learning_rate_init=0.0001, annealing=100, batch_size=None, shuffle=False):
        assert (self.hidden_layers == 2)

        # Mini-batching
        batches = []
        num_samples = self.xTrain.shape[0]

        if shuffle:
            indices = np.random.permutation(num_samples)
        else:
            indices = np.arange(num_samples)

        if batch_size == None:
            batch_size = num_samples

        for batch_num in range(num_samples // batch_size):
            indxs = indices[batch_num * batch_size:(batch_num + 1) * batch_size]
            batches.append((self.xTrain[indxs], self.yTrain[indxs]))

        W_hidden1 = self.weights[0]
        W_hidden2 = self.weights[1]
        W_output = self.weights[2]

        # Start a Timer for Training
        strt = time()
        print("Training...")

        # Iterate
        for epoch in range(max_epochs):
            # Decay Learning Rate
            alpha = learning_rate_init / (1 + epoch / annealing)

            # Iterate Over Mini-Batches
            for x_batch, t_batch in batches:
                # Forward Prop
                net_input_h1 = np.dot(x_batch, W_hidden1)
                hidden_layer_out1 = utilities.sigmoid_activation(net_input_h1)
                hidden_layer_out1 = np.insert(hidden_layer_out1, 0, 1, axis=1)

                net_input_h2 = np.dot(hidden_layer_out1, W_hidden2)
                hidden_layer_out2 = utilities.sigmoid_activation(net_input_h2)
                hidden_layer_out2 = np.insert(hidden_layer_out2, 0, 1, axis=1)

                net_input_o = np.dot(hidden_layer_out2, W_output)
                y = utilities.softmax_activation(net_input_o)

                # Back Prop (deltas)
                delta_output = (t_batch - y)
                delta_hidden2 = utilities.sigmoid_activation(net_input_h2) * (1 - utilities.sigmoid_activation(net_input_h2)) * np.dot(delta_output, W_output[1:,:].T)
                delta_hidden1 = utilities.sigmoid_activation(net_input_h1) * (1 - utilities.sigmoid_activation(net_input_h1)) * np.dot(delta_hidden2, W_hidden2[1:,:].T)

                # Gradient Descent
                W_output = W_output + alpha * np.dot(hidden_layer_out2.T, delta_output)
                W_hidden2 = W_hidden2 + alpha * np.dot(hidden_layer_out1.T, delta_hidden2)
                W_hidden1 = W_hidden1 + alpha * np.dot(x_batch.T, delta_hidden1)

                # Store the Model
                self.weights[0] = W_hidden1
                self.weights[1] = W_hidden2
                self.weights[2] = W_output

            # Get model predictions
            predictions_train = self.get_model_predictions(self.xTrain)
            predictions_valid = self.get_model_predictions(self.xValid)
            predictions_test = self.get_model_predictions(self.xTest)

            # Compute accuracies over epochs
            self.accuracies['train_acc'].append(utilities.accuracy(self.yTrain, predictions_train))
            self.accuracies['valid_acc'].append(utilities.accuracy(self.yValid, predictions_valid))
            self.accuracies['test_acc'].append(utilities.accuracy(self.yTest, predictions_test))

            # Cross-Entropy Loss over epochs
            self.losses['train_loss'].append(utilities.cross_entropy_loss(self.yTrain, predictions_train))
            self.losses['valid_loss'].append(utilities.cross_entropy_loss(self.yValid, predictions_valid))
            self.losses['test_loss'].append(utilities.cross_entropy_loss(self.yTest, predictions_test))

            # Debug statements
            if epoch % 10 == 0:
                print("\nEpoch:", epoch)
                print("\tAccuracy:", self.accuracies['train_acc'][-1])
                print("\tLoss:", self.losses['train_loss'][-1])

        print('\n\nTraining Done! Took', round(time() - strt, 3), " secs.")
        print('Final Training Accuracy: ', self.accuracies['train_acc'][-1], " in ", epoch, " epochs.")

        return 1

    def train(self, max_epochs=100, learning_rate_init=0.0001, annealing=100, batch_size=None, shuffle=False, gradient_checking=False, momentum=False):
        if self.hidden_layers == 1:
            self.train_hidden1(max_epochs=max_epochs, learning_rate_init=learning_rate_init, annealing=annealing,
                               batch_size=batch_size, shuffle=shuffle, gradient_checking=gradient_checking, momentum=momentum)

        elif self.hidden_layers == 2:
            self.train_hidden2(max_epochs=max_epochs, learning_rate_init=learning_rate_init, annealing=annealing,
                               batch_size=batch_size, shuffle=shuffle)

        return

    def get_numerical_gradient(self, x, t, layer_tag, weight_indices):
        """ Computes the numerical gradient for a given input with respect to a single weight specified by the tuple in
            weight_indices """
        assert (self.hidden_layers == 1)

        def evaluate(inputs, sigmoid_weights=None, softmax_weights=None):
            """ Perform Forward Prop with Curren Saved Weights
                Outputs Model Predictions for Data """
            assert (self.hidden_layers == 1)

            if type(sigmoid_weights) == type(np.array([0])):
                # Validates Inputs
                assert sigmoid_weights.shape[0] == inputs.shape[1], 'Invalid Dimensions with given Weights'

                # Layer 1
                net_input_h1 = np.dot(inputs, sigmoid_weights)
                hidden_layer_out1 = utilities.sigmoid_activation(net_input_h1)

            else:
                # Layer 1
                net_input_h1 = np.dot(inputs, self.weights[0])
                hidden_layer_out1 = utilities.sigmoid_activation(net_input_h1)

            hidden_layer_out1 = np.insert(hidden_layer_out1, 0, 1, axis=1)  # prepend bias term

            if type(softmax_weights) == type(np.array([0])):

                # Validates Inputs
                assert softmax_weights.shape[0] == hidden_layer_out1.shape[1], 'Invalid Dimensions with given Weights'

                # Output Layer
                net_input_o = np.dot(hidden_layer_out1, softmax_weights)
                y = utilities.softmax_activation(net_input_o)

            else:
                # Output Layer
                net_input_o = np.dot(hidden_layer_out1, self.weights[1])
                y = utilities.softmax_activation(net_input_o)

            return y

        epsilon = 0.01

        if layer_tag == 'hidden':

            sigmoid_weights_plus = np.copy(self.weights[0])
            sigmoid_weights_plus[weight_indices] += epsilon

            sigmoid_weights_minus = np.copy(self.weights[0])
            sigmoid_weights_minus[weight_indices] -= epsilon

            pred_plus = evaluate(x, sigmoid_weights=sigmoid_weights_plus)
            pred_minus = evaluate(x, sigmoid_weights=sigmoid_weights_minus)

            loss_plus = utilities.cross_entropy_loss(t, pred_plus)
            loss_minus = utilities.cross_entropy_loss(t, pred_minus)

            gradient = (loss_plus - loss_minus)/ (2 * epsilon)

            return gradient

        elif layer_tag == 'output':
            softmax_weights_plus = np.copy(self.weights[1])
            softmax_weights_plus[weight_indices] += epsilon

            softmax_weights_minus = np.copy(self.weights[1])
            softmax_weights_minus[weight_indices] -= epsilon

            pred_plus  = evaluate(x, sigmoid_weights=self.weights[0], softmax_weights=softmax_weights_plus)
            pred_minus = evaluate(x, sigmoid_weights=self.weights[0], softmax_weights=softmax_weights_minus)

            loss_plus = utilities.cross_entropy_loss(t, pred_plus)
            loss_minus = utilities.cross_entropy_loss(t, pred_minus)

            gradient = (loss_plus - loss_minus) / (2 * epsilon)

            return gradient

        else:
            print('Invalid Weights.  Input hidden or output.')

    def get_model_predictions(self, x):
        """ Perform Forward Prop with Curren Saved Weights
            Outputs Model Predictions for Data """

        if self.hidden_layers == 1:
            weights_hidden = self.best_model[1][0]
            weights_output = self.best_model[1][1]

            net_input_hidden = np.dot(x, weights_hidden)
            net_output_hidden = self.hidden_activation((net_input_hidden))
            net_output_hidden = np.insert(net_output_hidden, 0, 1, axis=1)

            predictions = self.output_activation(np.dot(net_output_hidden, weights_output))

        elif self.hidden_layers == 2:
            weights_hidden1 = self.best_model[1][0]
            weights_hidden2 = self.best_model[1][1]
            weights_output = self.best_model[1][2]

            net_input_hidden1 = np.dot(x, weights_hidden1)
            net_output_hidden1 = self.hidden_activation((net_input_hidden1))
            net_output_hidden1 = np.insert(net_output_hidden1, 0, 1, axis=1)

            net_input_hidden2 = np.dot(net_output_hidden1, weights_hidden2)
            net_output_hidden2 = self.hidden_activation((net_input_hidden2))
            net_output_hidden2 = np.insert(net_output_hidden2, 0, 1, axis=1)

            predictions = self.output_activation(np.dot(net_output_hidden2, weights_output))

        return predictions



























        '''
        if type(sigmoid_weights) == type(np.array([0])):
            # Validates Inputs
            assert sigmoid_weights.shape[0] == inputs.shape[1], 'Invalid Dimensions with given Weights'

            # Layer 1
            net_input_h1 = np.dot(inputs, sigmoid_weights)
            hidden_layer_out1 = utilities.sigmoid_activation(net_input_h1)

        else:
            # Layer 1
            net_input_h1 = np.dot(inputs, self.weights[0])
            hidden_layer_out1 = utilities.sigmoid_activation(net_input_h1)

        hidden_layer_out1 = np.insert(hidden_layer_out1, 0, 1, axis=1) # prepend bias term

        if type(softmax_weights) == type(np.array([0])):

            # Validates Inputs
            assert softmax_weights.shape[0] == hidden_layer_out1.shape[1], 'Invalid Dimensions with given Weights'

            # Output Layer
            net_input_o = np.dot(hidden_layer_out1, softmax_weights)
            y = utilities.softmax_activation(net_input_o)

        else:
            # Output Layer
            net_input_o = np.dot(hidden_layer_out1, self.weights[1])
            y = utilities.softmax_activation(net_input_o)

        return y
        '''

    def disp_train_accuracy(self):
        num_epochs = len(self.accuracy_over_epoch)

        plt.plot(np.arange(num_epochs), self.accuracy_over_epoch)
        plt.xlabel('Epochs')
        plt.ylabel('Training Accuracy')
        plt.title('Training Accuracy Over Epochs')
        plt.show()

        return None

    def disp_train_loss(self):
        num_epochs = len(self.loss_over_epoch)

        plt.plot(np.arange(num_epochs), self.loss_over_epoch)
        plt.xlabel('Epochs')
        plt.ylabel('Training Loss')
        plt.title('Training Cross-Entropy Loss Over Epochs')
        plt.show()

        return None

    def train_diagnostics(self, prob):

        plt.subplot(2, 1, 1)
        num_epochs = len(self.accuracies['train_acc'])

        plt.plot(np.arange(num_epochs), self.accuracies['train_acc'])
        plt.plot(np.arange(num_epochs), self.accuracies['valid_acc'])
        plt.plot(np.arange(num_epochs), self.accuracies['test_acc'])
        plt.xlabel('Epochs')
        plt.ylabel('Percent Accuracy')
        plt.title('Accuracy Vs. Epochs')
        plt.legend(['Training', 'Validation', 'Test'], loc='lower right')

        plt.subplot(2, 1, 2)
        plt.plot(np.arange(num_epochs), self.losses['train_loss'])
        plt.plot(np.arange(num_epochs), self.losses['valid_loss'])
        plt.plot(np.arange(num_epochs), self.losses['test_loss'])
        plt.xlabel('Epochs')
        plt.ylabel('Normalized Loss')
        plt.title('Cross-Entropy Loss Vs. Epochs')
        plt.legend(['Training', 'Validation', 'Test'], loc='upper right')

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)

        plt.savefig('report_images/' + prob + '.png')
        plt.show()

    def set_mlp_data(self, data):

        xTrain, yTrain, xValid, yValid, xTest, yTest = utilities.split_data(data)

        self.xTrain = xTrain
        self.yTrain = yTrain

        self.xValid = xValid
        self.yValid = yValid

        self.xTest = xTest
        self.yTest = yTest









