import numpy as np
from scipy.io import loadmat
from scipy.optimize import minimize
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn import svm
import datetime


def preprocess():
    """ 
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains 
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data 
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the 
       training set
     test_data: matrix of training set. Each row of test_data contains 
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args

    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    initialWeights = np.reshape(initialWeights, (n_features + 1, 1)) # 716 x 1
    
    # add bias in train_data
    train_data = np.column_stack([np.ones((n_data,1), dtype = np.uint8), train_data]) # 50000 x 716 
    
    z = np.dot(train_data,initialWeights) # 50000 x 1
    
    theta = sigmoid(z) # 50000 x 1
      
    prod1 = np.dot(labeli.T, np.log(theta))
    prod2 = np.dot((1 - labeli).T, np.log(1 - theta))
    prod = np.add(prod1, prod2)
    
    error = (-1/n_data) * np.sum(prod)
    print(error)
    
    error_grad = np.dot(train_data.T,np.subtract(theta, labeli))
    error_grad = (1/n_data) * error_grad
    error_grad = error_grad.flatten()

    return error, error_grad


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W 
     of Logistic Regression
     
     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight 
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D
         
     Output: 
         label: vector of size N x 1 representing the predicted label of 
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    m = data.shape[0] # number of training data
    
    # add bias in train_data
    data = np.column_stack([np.ones((m,1), dtype = np.uint8), data]) # 50000 x 716 
    
    z = np.dot(data,W) # 50000 x 10
    
    theta = sigmoid(z) # 50000 x 10
    
    label = np.argmax(theta, axis = 1)
    label = np.reshape(label, (data.shape[0], 1))

    return label

def mlrObjFunction(params, *args):
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights_b: the weight vector of size (D + 1) x 10
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    train_data, labeli = args
    n_data = train_data.shape[0]
    n_feature = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_feature + 1, n_class))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    ones_bias = np.ones((n_data, 1))

    train_data = np.concatenate((ones_bias, train_data), axis=1) #50000 x 716

    # reshaping
    W = params.reshape(n_feature + 1, n_class) #716 x 10

    #theta matrix
    theta = np.zeros((n_data, n_class))

    dot_product_W_X = np.dot(train_data, W) #50000 x 10

    theta_matrix_sum = np.sum(np.exp(dot_product_W_X), axis=1).reshape(n_data, 1) #50000 x 10

    theta_matrix = (np.exp(dot_product_W_X) / theta_matrix_sum) #50000 x 10

    # log
    log_theta_matrix = np.log(theta_matrix) #50000 x 10

    # The likelihood function with the negative logarithm Equation(7)
    error = (-1) * np.sum(np.sum(labeli * log_theta_matrix))

    #gradient descent calculation
    subtract_theta_y = theta_matrix - labeli

    error_grad = (np.dot(train_data.T, subtract_theta_y))

    error = error / n_data
    error_grad = error_grad / n_data
    
    error_grad = error_grad.flatten()

    return error, error_grad


def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    
    ones_bias = np.ones((data.shape[0], 1))
    train_data = np.concatenate((ones_bias, data), axis=1)


    dot_product_W_X = np.dot(train_data, W)


    theta_matrix_sum = np.sum(np.exp(dot_product_W_X))

    posterior = np.exp(dot_product_W_X) / theta_matrix_sum

    for i in range(posterior.shape[0]):
        label[i] = np.argmax(posterior[i])
    label = label.reshape(label.shape[0], 1)

    return label


"""
Script for Logistic Regression
"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# number of classes
n_class = 10

# number of training samples
n_train = train_data.shape[0]

# number of features
n_feature = train_data.shape[1]

Y = np.zeros((n_train, n_class))
for i in range(n_class):
    Y[:, i] = (train_label == i).astype(int).ravel()

# Logistic Regression with Gradient Descent
W = np.zeros((n_feature + 1, n_class))
initialWeights = np.zeros((n_feature + 1, 1))
opts = {'maxiter': 100}
for i in range(n_class):
    labeli = Y[:, i].reshape(n_train, 1)
    args = (train_data, labeli)
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)
    W[:, i] = nn_params.x.reshape((n_feature + 1,))

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')

"""
Script for Support Vector Machine
"""

print('\n\n--------------SVM-------------------\n\n')
##################
# YOUR CODE HERE #
##################

np.random.seed = 100

X_train = []
y_train = []
for i in range(10):
    x = train_data[np.where(train_label == i)[0]]
    np.random.shuffle(x)
    X_train.extend(x[:1000])
    y_train.extend([i] * 1000)
X_train = np.asarray(X_train)
y_train = np.asarray(y_train)

randomize = np.arange(10000)
np.random.shuffle(randomize)
X_train = X_train[randomize]
y_train = y_train[randomize]

start = datetime.datetime.now()
svm_fit1 = svm.LinearSVC().fit(X_train, y_train)
end = datetime.datetime.now()
diff = end - start
print("total time taken =", diff.total_seconds())
accuracy1 = svm_fit1.score(X_train, y_train)
accuracy2 = svm_fit1.score(validation_data, validation_label)
accuracy3 = svm_fit1.score(test_data, test_label)
print('SVM Linear Accuracy on training data', accuracy1) #0.9632
print('SVM Linear Accuracy on validation data', accuracy2) #0.8888
print('SVM Linear Accuracy on testing data', accuracy3) #0.8934

start = datetime.datetime.now()
svm_fit2 = svm.SVC(kernel='rbf').fit(X_train, y_train)
end = datetime.datetime.now()
diff = end - start
print("total time taken =", diff.total_seconds())
accuracy1 = svm_fit2.score(X_train, y_train)
print('SVM Default RBF Accuracy on train data', accuracy1) #9245
accuracy2 = svm_fit2.score(validation_data, validation_label) 
print('SVM Default RBF Accuracy on validation data', accuracy2) # 0.9191
accuracy3 = svm_fit2.score(test_data, test_label)
print('SVM Default RBF Accuracy on test data', accuracy3) #9241

start = datetime.datetime.now()
svm_fit3 = svm.SVC(kernel='rbf', gamma=1).fit(X_train, y_train)
end = datetime.datetime.now()
diff = end - start
print("total time taken =", diff.total_seconds())
accuracy1 = svm_fit3.score(X_train, y_train)
accuracy2 = svm_fit3.score(validation_data, validation_label)
accuracy3 = svm_fit3.score(test_data, test_label)
print('SVM RBF gamma 1 Accuracy on training data', accuracy1) #1.0
print('SVM RBF gamma 1 Accuracy on validation data', accuracy2) # 0.1763
print('SVM RBF gamma 1 Accuracy on test data', accuracy3) #0.1848

c = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
acc_train = []
acc_val = []
acc_test = []
time = []
for C in c:
    start = datetime.datetime.now()
    svm_fit4 = svm.SVC(kernel='rbf', C=C).fit(X_train, y_train)
    end = datetime.datetime.now()
    diff = end - start
    print("\n total time taken =", diff.total_seconds())
    time.append(diff.total_seconds())
    acc_tr = svm_fit4.score(X_train, y_train)
    acc_train.append(acc_tr)
    acc_v = svm_fit4.score(validation_data, validation_label)
    acc_val.append(acc_v)
    acc_te = svm_fit4.score(test_data, test_label)
    acc_test.append(acc_te)

#print("Training accuracies : ", acc_train) #[0.9245, 0.9633, 0.977, 0.9836, 0.9886, 0.992, 0.9933, 0.9955, 0.9966, 0.9974, 0.998]
#print("Validation accuracies : ", acc_val) #[0.9191, 0.9419, 0.9461, 0.9462, 0.9459, 0.9457, 0.9465, 0.9475, 0.9465, 0.9465, 0.9452]
#print("Testing accuracies : ", acc_test) #[0.9241, 0.9444, 0.9463, 0.9471, 0.9477, 0.9474, 0.9479, 0.9479, 0.9481, 0.9476, 0.9469]
#print("Time taken : ", time) #[32.657474, 17.101036, 15.017569, 14.398448, 14.234215, 14.103541, 14.143062, 14.267995, 14.067935, 14.061249, 14.152245]
    
fig = plt.figure(figsize=(12, 9), dpi= 80)
ax = plt.axes()
ax.plot(c, acc_train, label='Training Data')
ax.plot(c, acc_test, label='Test Data')
ax.plot(c, acc_val, label='Validation Data')
plt.grid(alpha=0.3)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel('C', fontsize=16)
plt.ylabel('Accuracy', fontsize=16)
ax2 = ax.twinx()
ax2.plot(c, time, label='Time Taken', color='k')
ax.legend(loc='center right', ncol=3, fancybox=True)
ax2.legend(loc='lower right', ncol=1, fancybox=True)
plt.title('Accuracy vs C', fontsize=20)
plt.yticks(fontsize=12)
plt.ylabel('Time Taken (secs)', fontsize=16)
plt.axvspan(60, 70, color='lightblue', alpha=0.3)
plt.show()


"""
Script for Extra Credit Part
"""
# FOR EXTRA CREDIT ONLY
W_b = np.zeros((n_feature + 1, n_class))
initialWeights_b = np.zeros((n_feature + 1, n_class))
opts_b = {'maxiter': 100}

args_b = (train_data, Y)
nn_params = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b, method='CG', options=opts_b)
W_b = nn_params.x.reshape((n_feature + 1, n_class))

# Find the accuracy on Training Dataset
predicted_label_b = mlrPredict(W_b, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label_b = mlrPredict(W_b, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label_b = mlrPredict(W_b, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')
