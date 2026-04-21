import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os

def train():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'diabet_clean.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    print("Membaca dataset diabetes...")
    df = pd.read_csv(file_path)

    # Encode gender
    print("Encoding gender...")
    le_gender = LabelEncoder()
    df['gender'] = le_gender.fit_transform(df['gender'])

    # Encode smoking_history
    print("Encoding smoking_history...")
    le_smoking = LabelEncoder()
    df['smoking_history'] = le_smoking.fit_transform(df['smoking_history'])

    # Features and Target
    X = df[['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']]
    y = df['diabetes']

    print("Standardizing data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Training model KNN...")
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_scaled, y)

    print("Menyimpan model, scaler, dan encoder...")
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(knn, os.path.join(models_dir, 'model_knn_diabetes.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler_diabetes.pkl'))
    joblib.dump(le_gender, os.path.join(models_dir, 'le_gender_diabetes.pkl'))
    joblib.dump(le_smoking, os.path.join(models_dir, 'le_smoking_diabetes.pkl'))
    
    print("Selesai! Model diabetes berhasil di-export.")

if __name__ == "__main__":
    train()
