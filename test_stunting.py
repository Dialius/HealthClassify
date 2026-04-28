import joblib
import numpy as np
import pandas as pd

knn_model = joblib.load('models/model_knn.pkl')
scaler = joblib.load('models/scaler.pkl')

umur = 36
jk = 0
tinggi = 69.9

X_baru = np.array([[umur, jk, tinggi]])
X_scaled = scaler.transform(X_baru)

distances, indices = knn_model.kneighbors(X_scaled)
print("Neighbors indices:", indices)

df = pd.read_csv('data/balita_fix.csv')
for idx in indices[0]:
    print(df.iloc[idx].to_dict())
