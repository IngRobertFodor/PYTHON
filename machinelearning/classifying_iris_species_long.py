from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import numpy as np


iris_dataset = load_iris()

print("Keys of iris_dataset: \n{}".format(iris_dataset.keys()))
print()
print(iris_dataset['DESCR'][:193] + "\n...")
print()
print("Target names: {}".format(iris_dataset['target_names']))
print()
print("Feature names: \n{}".format(iris_dataset['feature_names']))
print()
print("We see that the array contains measurements for 150 different flowers.")
print()
print("Remember that the individual items are called  SAMPLES  in machine learning,")
print("and their properties are called  FEATURES.")
print()
print("The shape of the data array is the number of samples multiplied by the number of features.")
print("This is a convention in scikit-learn.")
print()
print("Here are the feature values for the first five samples:")
print("First five columns of data:\n{}".format(iris_dataset['data'][:5]))
print()
print("The species are encoded as integers from 0 to 2.")
print("The meanings of the numbers are given by the iris['target_names'] array.")
print("0 means setosa, 1 means versicolor, and 2 means virginica.")
print("Target:\n{}".format(iris_dataset['target']))

print()
print()
print("     Start training the model.")
print()
# from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    iris_dataset['data'], iris_dataset['target'], random_state=0)
# X is the input to a function and y is the output.
print("X_train shape: {}".format(X_train.shape))
print("y_train shape: {}".format(y_train.shape))
print("X_test shape: {}".format(X_test.shape))
print("y_test shape: {}".format(y_test.shape))

print()
print()
print("     Building Your First Model: k-Nearest Neighbors.")
print()
# from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=1)
building_model = knn.fit(X_train, y_train)
print(building_model)

print()
print()
print("!! Making Predictions. !!")
print("! This is for demo purposes only. !")
print()
# We can now make predictions using this model on new data.
X_new = np.array([[5, 2.9, 1, 0.2]])
print("X_new shape: {}".format(X_new.shape))
prediction = knn.predict(X_new)
print("Prediction: {}".format(prediction))
print("Predicted target name: {}".format(iris_dataset['target_names'][prediction]))

print()
print()
print("     Evaluating the Model")
print()
y_pred = knn.predict(X_test)
print("Test set predictions:\n {}".format(y_pred))
# Test Set Score
print("Test set score: {:.2f}".format(np.mean(y_pred == y_test)))
# Test Set Score: Differently
print("Test set score: {:.2f}".format(knn.score(X_test, y_test)))