import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os

def train():
    # Menggunakan path absolut berdasarkan lokasi file agar bisa dijalankan dari folder manapun
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'balita_fix.csv')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    print("Membaca dataset...")
    df = pd.read_csv(file_path)

    print("Encoding Jenis Kelamin...")
    le_jk = LabelEncoder()
    # Pastikan nama kolom sesuai
    if "Jenis Kelamin" in df.columns:
        df["Jenis Kelamin"] = le_jk.fit_transform(df["Jenis Kelamin"])
    else:
        print("Kolom 'Jenis Kelamin' tidak ditemukan.")
        return

    print("Encoding Status Gizi (Target)...")
    le_status = LabelEncoder()
    if "Status Gizi" in df.columns:
        df["Status Gizi"] = le_status.fit_transform(df["Status Gizi"])
    else:
        print("Kolom 'Status Gizi' tidak ditemukan.")
        return

    X = df[['Umur', 'Jenis Kelamin', 'Tinggi Badan']]
    y = df['Status Gizi']

    print("Standardizing data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Training model KNN...")
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_scaled, y)

    print("Menyimpan model, scaler, dan encoder...")
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(knn, os.path.join(models_dir, 'model_knn.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    joblib.dump(le_status, os.path.join(models_dir, 'label_encoder.pkl'))
    
    # Save the Jenis Kelamin Label Encoder as well if we need to predict using strings like "Laki-laki" from UI
    # But usually frontend will send 0 or 1 directly if we set the value="0" in HTML.
    
    print("Selesai! Model berhasil di-export.")

if __name__ == "__main__":
    train()
