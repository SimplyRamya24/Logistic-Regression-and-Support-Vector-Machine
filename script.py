# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from math import sqrt
from sklearn.svm import SVC
import pickle

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

     Some suggestions for preprocessing step:
     - divide the original data set to training, validation and testing set
           with corresponding labels
     - convert original data set from integer to double by using double()
           function
     - normalize the data to [0, 1]
     - feature selection
    """
    
    mat = loadmat('mnist_all.mat'); #loads the MAT object as a Dictionary
    
    n_feature = mat.get("train1").shape[1];
    n_sample = 0;
    for i in range(10):
        n_sample = n_sample + mat.get("train"+str(i)).shape[0];
    n_validation = 1000;
    n_train = n_sample - 10*n_validation;
    
    # Construct validation data
    validation_data = np.zeros((10*n_validation,n_feature));
    for i in range(10):
        validation_data[i*n_validation:(i+1)*n_validation,:] = mat.get("train"+str(i))[0:n_validation,:];
        
    # Construct validation label
    validation_label = np.ones((10*n_validation,1));
    for i in range(10):
        validation_label[i*n_validation:(i+1)*n_validation,:] = i*np.ones((n_validation,1));
    
    # Construct training data and label
    train_data = np.zeros((n_train,n_feature));
    train_label = np.zeros((n_train,1));
    temp = 0;
    for i in range(10):
        size_i = mat.get("train"+str(i)).shape[0];
        train_data[temp:temp+size_i-n_validation,:] = mat.get("train"+str(i))[n_validation:size_i,:];
        train_label[temp:temp+size_i-n_validation,:] = i*np.ones((size_i-n_validation,1));
        temp = temp+size_i-n_validation;
        
    # Construct test data and label
    n_test = 0;
    for i in range(10):
        n_test = n_test + mat.get("test"+str(i)).shape[0];
    test_data = np.zeros((n_test,n_feature));
    test_label = np.zeros((n_test,1));
    temp = 0;
    for i in range(10):
        size_i = mat.get("test"+str(i)).shape[0];
        test_data[temp:temp+size_i,:] = mat.get("test"+str(i));
        test_label[temp:temp+size_i,:] = i*np.ones((size_i,1));
        temp = temp + size_i;
    
    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis = 0);
    index = np.array([]);
    for i in range(n_feature):
        if(sigma[i] > 0.001):
            index = np.append(index, [i]);
    train_data = train_data[:,index.astype(int)];
    validation_data = validation_data[:,index.astype(int)];
    test_data = test_data[:,index.astype(int)];

    # Scale data to 0 and 1
    train_data = train_data/255.0;
    validation_data = validation_data/255.0;
    test_data = test_data/255.0;
    
    return train_data, train_label, validation_data, validation_label, test_data, test_label

def sigmoid(z):
    return 1.0/(1.0 + np.exp(-z));
    
def blrObjFunction(params, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args;
    n_feature = train_data.shape[1];
    Wt = params.reshape(n_feature+1,1);
    error_grad = np.zeros((n_feature+1,1))
     
    #add bias
    X_bias = np.column_stack((np.ones(train_data.shape[0]),train_data))
    X_fin = np.transpose(X_bias)
    W_t = np.transpose(Wt)   
    P_C1 = sigmoid(np.dot(W_t,X_fin))
    yn = np.transpose(P_C1)
    oneminuslabeli = np.subtract(1,labeli)
    oneminusyn = np.subtract(1,yn)
    error = -1*np.sum(labeli*np.log(yn)+oneminuslabeli*np.log(oneminusyn))
    ynminuslabeli = np.subtract(yn,labeli)
    error_grad = np.dot(X_fin,ynminuslabeli)
    error_grad = error_grad.reshape(error_grad.shape[0])
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
    #label = np.zeros((data.shape[0],1));
    x_bias = np.column_stack((np.ones(data.shape[0]),data))
    wt = np.transpose(W)
    x_fin = np.transpose(x_bias)
    label = np.argmax(np.dot(wt,x_fin),0)
    label = label.reshape(label.shape[0],1)
    return label


"""
Script for Logistic Regression
"""
train_data, train_label, validation_data,validation_label, test_data, test_label = preprocess();

# number of classes
n_class = 10;

# number of training samples
n_train = train_data.shape[0];

# number of features
n_feature = train_data.shape[1];

T = np.zeros((n_train, n_class));
for i in range(n_class):
    T[:,i] = (train_label == i).astype(int).ravel();
    
# Logistic Regression with Gradient Descent
W = np.zeros((n_feature+1, n_class));
initialWeights = np.zeros((n_feature+1,1));
opts = {'maxiter' : 50};
for i in range(n_class):
    labeli = T[:,i].reshape(n_train,1);
    args = (train_data, labeli);
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args,method='CG', options=opts)
    W[:,i] = nn_params.x.reshape((n_feature+1,));

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data);
print('\n Training set Accuracy:' + str(100*np.mean((predicted_label == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data);
print('\n Validation set Accuracy:' + str(100*np.mean((predicted_label == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data);
print('\n Testing set Accuracy:' + str(100*np.mean((predicted_label == test_label).astype(float))) + '%')

pickle.dump(W,open('params.pickle','wb'))

"""
Script for Support Vector Machine
"""

print('\n\n--------------SVM-------------------\n\n')

train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()
acc1 = np.zeros(11)
acc2 = np.zeros(11)

# Using linear kernel (all other parameters are kept default).
clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
    gamma=0.0, kernel='linear', max_iter=-1, probability=False,
    random_state=None, shrinking=True, tol=0.001, verbose=False)
clf.fit(train_data, train_label.ravel()) 

print('\n Using linear kernel (all other parameters are kept default)') 
print('Validation set Accuracy: '+ str(clf.score(validation_data, validation_label.ravel())*100)+'%') 
print('Testing set Accuracy: '+ str(clf.score(test_data, test_label.ravel())*100)+'%')


#Using radial basis function with value of gamma setting to 1 (all other parameters are kept default).
clf2 = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
    gamma=1.0, kernel='rbf', max_iter=-1, probability=False,
    random_state=None, shrinking=True, tol=0.001, verbose=False)
clf2.fit(train_data, train_label.ravel()) 

print('\n Using radial basis function with value of gamma setting to 1 (all other parameters are kept default)') 
print('Validation set Accuracy: '+ str(clf2.score(validation_data, validation_label.ravel())*100)+'%') 
print('Testing set Accuracy: '+ str(clf2.score(test_data, test_label.ravel())*100)+'%')

# Using radial basis function with value of gamma setting to default (all other parameters are kept default).
clf3 = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
    gamma=0.0, kernel='rbf', max_iter=-1, probability=False,
    random_state=None, shrinking=True, tol=0.001, verbose=False)
clf3.fit(train_data, train_label.ravel()) 

acc1[0] = clf3.score(validation_data, validation_label.ravel())*100
acc2[0] = clf3.score(test_data, test_label.ravel())*100
print('\n Using radial basis function with value of gamma setting to default (all other parameters are kept default)') 
print('Validation set Accuracy: '+ str(acc1[0])+'%') 
print('Testing set Accuracy: '+ str(acc2[0])+'%')


#Using radial basis function with value of gamma setting to default and varying value of C (1, 10, 20, 30, · · · , 100)
count = 1
for i in range(10,101,10):
    clf = SVC(C=float(i), cache_size=200, class_weight=None, coef0=0.0, degree=3,
        gamma=0.0, kernel='rbf', max_iter=-1, probability=False,
        random_state=None, shrinking=True, tol=0.001, verbose=False)
    clf.fit(train_data, train_label.ravel()) 

    acc1[count] = clf.score(validation_data, validation_label)*100
    acc2[count] = clf.score(test_data, test_label)*100
    count = count + 1

print('\n Using radial basis function with value of gamma setting to default and varying value of C (1, 10, 20, 30, · · · , 100)') 
print('Validation set Accuracy: '+ str(acc1)+'%') 
print('Testing set Accuracy: '+ str(acc2)+'%')
