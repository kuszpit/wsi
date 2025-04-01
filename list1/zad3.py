import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from torchvision import datasets, transforms

data_transform = transforms.Compose([
    transforms.ToTensor()
])

train_dataset = datasets.MNIST(root="./data", train=True, download=True, transform=data_transform)
test_dataset = datasets.MNIST(root="./data", train=False, download=True, transform=data_transform)

def prepare_data_for_rf():
    X_train = np.array([img.numpy().flatten() for img, _ in train_dataset])
    y_train = np.array([label for _, label in train_dataset])
    X_test = np.array([img.numpy().flatten() for img, _ in test_dataset])
    y_test = np.array([label for _, label in test_dataset])
    return X_train, y_train, X_test, y_test

X_train, y_train, X_test, y_test = prepare_data_for_rf()

clf = RandomForestClassifier(n_estimators=100, random_state=42)

clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print(classification_report(y_test, y_pred))