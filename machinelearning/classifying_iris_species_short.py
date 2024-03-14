from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


iris_dataset = load_iris()

print("     Start training the model.")
# from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    iris_dataset['data'], iris_dataset['target'], random_state=0)
# X is the input to a function and y is the output.

print("     Building Your First Model: k-Nearest Neighbors.")
# from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(X_train, y_train)

print("     Evaluating the Model")
print("Test set score: {:.2f}".format(knn.score(X_test, y_test)))