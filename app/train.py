"""Run this once to generate the model file: python train.py"""
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pickle

iris = load_iris()
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(iris.data, iris.target)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved to model.pkl")
