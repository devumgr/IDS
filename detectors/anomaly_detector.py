import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.scaler = StandardScaler()

    def fit(self, X):
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        # Fit the model
        self.model.fit(X_scaled)

    def predict(self, X):
        # Scale the data
        X_scaled = self.scaler.transform(X)
        # Predict anomalies
        return self.model.predict(X_scaled)

    def score_samples(self, X):
        # Scale the data
        X_scaled = self.scaler.transform(X)
        # Get anomaly scores
        return self.model.score_samples(X_scaled)
    