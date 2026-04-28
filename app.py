from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import requests

import os
from datetime import datetime
import random
from pymongo import MongoClient

app = Flask(__name__)
# Memuat model yang sudah dilatih
try:
    knn_model = joblib.load('models/model_knn.pkl')
    scaler = joblib.load('models/scaler.pkl')
    le_status = joblib.load('models/label_encoder.pkl')
except Exception as e:
    print(f"Error loading models. Make sure you have run scripts/train_stunting.py first. Error: {e}")

try:
    knn_model_diabetes = joblib.load('models/model_knn_diabetes.pkl')
    scaler_diabetes = joblib.load('models/scaler_diabetes.pkl')
    le_gender_diabetes = joblib.load('models/le_gender_diabetes.pkl')
    le_smoking_diabetes = joblib.load('models/le_smoking_diabetes.pkl')
except Exception as e:
    print(f"Error loading diabetes models. Make sure you have run scripts/train_diabetes.py first. Error: {e}")

import os
from dotenv import load_dotenv

load_dotenv()

# Kunci API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Setup MongoDB
MONGO_URI = os.environ.get("MONGODB_URI")
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client["health_classify"]
    history_collection = db["history"]
except Exception as e:
    print(f"MongoDB connection error: {e}")
    history_collection = None

def get_backup_recommendation(status_gizi):
    """Sistem Pakar Lokal sebagai backup terakhir jika semua API mati."""
    status = str(status_gizi).lower()
    if status == 'sangat stunting' or status == 'severely stunted' or status == 'sangat pendek':
        return ("* **Konsultasi Medis Segera:** Mari segera jadwalkan kunjungan ke Dokter Spesialis Anak untuk observasi komprehensif dan intervensi gizi medis khusus.\n"
                "* **Prioritaskan Asupan Protein Hewani:** Sangat disarankan memberikan sumber protein adekuat seperti telur, ikan, daging, atau susu formula khusus sesuai rekomendasi medis.\n"
                "* **Jaga Protokol Kebersihan:** Anak pada kondisi ini rentan terhadap infeksi. Mohon pastikan sterilisasi alat makannya dan terapkan kebersihan lingkungan.")
    elif status == 'stunting' or status == 'stunted' or status == 'pendek':
        return ("* **Modifikasi Porsi Gizi Seimbang:** Tingkatkan kepadatan kalori dan protein hewani (seperti telur atau ikan) pada setiap jadwal makanan utamanya.\n"
                "* **Pemantauan Antropometri Rutin:** Sangat penting bagi Bapak/Ibu untuk rutin memantau kurva pertumbuhan tinggi dan berat badannya setiap bulan di faskes terdekat.\n"
                "* **Berikan Stimulasi Berkelanjutan:** Bantu maksimalkan potensi pertumbuhannya dengan mengajak anak aktif bergerak dan bermain sesuai usianya setiap hari.")
    elif status == 'tinggi':
        return ("* **Optimalkan Pola Asuh Gizi:** Pertahankan pemberian nutrisi makro maupun mikro agar selalu menunjang laju pertumbuhan fisiknya secara proporsional.\n"
                "* **Fasilitasi Aktivitas Fisik:** Ajak ananda rutin berlatih fisik ringan guna memperkuat fungsi motorik kasar dan kepadatan tulangnya.\n"
                "* **Observasi Kurva Pertumbuhan:** Tetap pantau indikator berat badannya secara periodik agar terus selaras dan ideal di kurva standar deviasi WHO.")
    else:
        return ("* **Pertahankan Kepatuhan Menu Sehat:** Tetap aplikasikan pedoman gizi seimbang secara konsisten agar kebutuhan nutrisi bulanannya selalu tercukupi secara optimal.\n"
                "* **Edukasi Perilaku Bersih & Sehat (PHBS):** Cegah paparan patogen dengan rutin mempraktikkan cuci tangan serta menjaga kebersihan sanitasi domestik.\n"
                "* **Kepatuhan Jadwal Imunisasi:** Pastikan jadwal imunisasi dan asupan suplementasi vitamin perlindungannya selalu lengkap sesuai buku KIA.")

def get_groq_recommendation(umur, jk_text, tinggi, status_gizi):
    """Fungsi mengambil saran dari Groq API (Llama3-8b)."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""
    Berperanlah sebagai Dokter Spesialis Anak (Pediatrician) dengan keahlian dan pengalaman klinis puluhan tahun.
    Seorang pasien balita berusia {umur} bulan, berjenis kelamin {jk_text}, dengan tinggi badan {tinggi} cm saat ini 
    terdiagnosis dengan kelas status gizi: {status_gizi}.
    
    Berikan edukasi medis serta maksimal 3 poin saran penanganan klinis, anjuran asupan nutrisi secara spesifik (harus makan apa/menu harian yang baik), dan pola asuh suportif untuk panduan orang tua. 
    Gunakan gaya bahasa yang sangat profesional, sangat empatik, menenangkan, dokter-sentris, namun tetap mudah dipahami awam.
    Jawab langsung pada intinya menggunakan Markdown bullet points, tanpa kalimat pembuka/penutup basa-basi.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result_json = response.json()
        return result_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API Error: {e}. Menggunakan sistem backup AI lokal.")
        return get_backup_recommendation(status_gizi)

def get_gemini_recommendation(umur, jk_text, tinggi, status_gizi):
    """Fungsi pembantu untuk memanggil Google Gemini REST API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    Berperanlah sebagai Dokter Spesialis Anak (Pediatrician) dengan keahlian dan pengalaman klinis puluhan tahun.
    Seorang pasien balita berusia {umur} bulan, berjenis kelamin {jk_text}, dengan tinggi badan {tinggi} cm saat ini 
    terdiagnosis dengan kelas status gizi: {status_gizi}.
    
    Berikan edukasi medis serta maksimal 3 poin saran penanganan klinis, anjuran asupan nutrisi secara spesifik (harus makan apa/menu harian yang baik), dan pola asuh suportif untuk panduan orang tua. 
    Gunakan gaya bahasa yang sangat profesional, sangat empatik, menenangkan, dokter-sentris, namun tetap mudah dipahami awam.
    Jawab langsung pada intinya menggunakan Markdown bullet points, tanpa kalimat pembuka/penutup basa-basi.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result_json = response.json()
        
        # Ekstrak jawaban dari response structure Gemini API
        ai_response = result_json['candidates'][0]['content']['parts'][0]['text']
        return ai_response
    except Exception as e:
        print(f"Gemini API Error/Timeout: {e}. Beralih menggunakan Groq API Backup.")
        return get_groq_recommendation(umur, jk_text, tinggi, status_gizi)

def get_backup_recommendation_diabetes(prediction_text):
    if prediction_text == "Positif Diabetes":
        return "* **Segera Konsultasi Medis:** Kami sangat menyarankan Anda segera berkonsultasi dengan dokter untuk pemeriksaan gula darah lanjutan (seperti tes toleransi glukosa atau HbA1c ulang) dan perencanaan tata laksana medis.\n* **Modifikasi Gaya Hidup Segera:** Terapkan pola makan sehat dengan mengurangi asupan gula, karbohidrat sederhana, dan makanan olahan.\n* **Rutin Periksa Gula Darah:** Pantau kadar gula darah secara teratur sesuai petunjuk tenaga medis serta mulai rutinitas olahraga fisik ringan secara bertahap."
    else:
        return "* **Pertahankan Gaya Hidup Sehat:** Pertahankan pola asupan makanan bergizi seimbang, kaya serat dan rendah gula tambahan.\n* **Lakukan Aktivitas Fisik Rutin:** Setidaknya 150 menit per minggu aktivitas aerobik sedang (seperti jalan cepat) untuk menjaga sensitivitas insulin yang optimal.\n* **Skrining Berkala:** Lakukan pemeriksaan medis tahunan dan pantau indeks massa tubuh (BMI) Anda agar selalu dalam batas sehat."

def get_groq_recommendation_diabetes(data, prediction_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""
    Sebagai dokter endokrinologis profesional, berikan penjelasan medis yang empatik tentang hasil prediksi diabetes ini.
    Data profil pasien:
    - BMI: {data.get('bmi')}
    - HbA1c: {data.get('HbA1c_level')}%
    - Glukosa Darah: {data.get('blood_glucose_level')} mg/dL
    Analisis Sistem: {prediction_text}
    
    Berikan maksimal 3 bullet points tindakan lanjutan, anjuran spesifik pola makan (harus makan apa/yang harus dihindari), dan saran gaya hidup. Gunakan nada yang menenangkan namun sangat profesional.
    """
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API Error Diabetes: {e}")
        return get_backup_recommendation_diabetes(prediction_text)

def get_gemini_recommendation_diabetes(data, prediction_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Sebagai dokter endokrinologis profesional, berikan penjelasan medis yang empatik tentang hasil prediksi diabetes ini.
    Data profil pasien:
    - BMI: {data.get('bmi')}
    - HbA1c: {data.get('HbA1c_level')}%
    - Glukosa Darah: {data.get('blood_glucose_level')} mg/dL
    Analisis Sistem: {prediction_text}
    
    Berikan maksimal 3 bullet points tindakan lanjutan, anjuran spesifik pola makan (harus makan apa/yang harus dihindari), dan saran gaya hidup. Gunakan nada yang menenangkan namun sangat profesional.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Gemini API Error Diabetes: {e}")
        return get_groq_recommendation_diabetes(data, prediction_text)

@app.route('/')
def home():
    # Menampilkan file HTML (Portal Pemilihan Form)
    return render_template('home.html')

@app.route('/diabetes')
def diabetes():
    # Menampilkan form diabetes
    return render_template('diabetes.html')

@app.route('/stunting')
def stunting():
    # Menampilkan form stunting
    return render_template('stunting.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        umur = float(data.get('umur', 0))
        jk = int(data.get('jenis_kelamin', 0)) # 0 Laki-laki, 1 Perempuan
        tinggi = float(data.get('tinggi_badan', 0))
        
        # 1. Transform input array
        X_baru = np.array([[umur, jk, tinggi]])
        X_scaled = scaler.transform(X_baru)
        
        # 2. Prediksi KNN
        prediction_encoded = knn_model.predict(X_scaled)
        prediction_label = le_status.inverse_transform(prediction_encoded)[0]
        
        stunting_map = {
            'normal': 'Normal',
            'severely stunted': 'Sangat Pendek',
            'stunted': 'Pendek',
            'tinggi': 'Tinggi'
        }
        prediction_label_id = stunting_map.get(prediction_label.lower(), prediction_label.title())
        
        # 3. Panggil AI untuk rekomendasi (Gemini -> Groq -> Lokal)
        jk_text = "Laki-laki" if jk == 0 else "Perempuan"
        ai_recomendation = get_gemini_recommendation(umur, jk_text, tinggi, prediction_label_id)
        
        doc_id = str(random.randint(100000, 999999))
        if history_collection is not None:
            try:
                history_collection.insert_one({
                    "doc_id": doc_id,
                    "type": "Stunting",
                    "result": prediction_label_id,
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                print(f"Failed to save history: {e}")
        
        return jsonify({
            'status': 'success',
            'prediksi_gizi': prediction_label_id,
            'ai_saran': ai_recomendation,
            'doc_id': doc_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    try:
        data = request.json
        
        gender_val = le_gender_diabetes.transform([data['gender']])[0]
        smoking_val = le_smoking_diabetes.transform([data['smoking_history']])[0]
        
        X_baru = np.array([[
            float(gender_val),
            float(data['age']),
            float(data['hypertension']),
            float(data['heart_disease']),
            float(smoking_val),
            float(data['bmi']),
            float(data['HbA1c_level']),
            float(data['blood_glucose_level'])
        ]])
        
        X_scaled = scaler_diabetes.transform(X_baru)
        prediction = knn_model_diabetes.predict(X_scaled)[0]
        prediction_text = "Positif Diabetes" if prediction == 1 else "Negatif Diabetes"
        
        ai_recommendation = get_gemini_recommendation_diabetes(data, prediction_text)
        
        doc_id = str(random.randint(100000, 999999))
        if history_collection is not None:
            try:
                history_collection.insert_one({
                    "doc_id": doc_id,
                    "type": "Diabetes",
                    "result": prediction_text,
                    "timestamp": datetime.utcnow()
                })
            except Exception as e:
                print(f"Failed to save history: {e}")
        
        return jsonify({
            'status': 'success',
            'prediction': prediction_text,
            'recommendation': ai_recommendation,
            'doc_id': doc_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    if history_collection is None:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    try:
        records = history_collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(5)
        history_list = []
        for r in records:
            # Format timestamp
            r['timestamp'] = r['timestamp'].strftime("%Y-%m-%d %H:%M:%S UTC")
            history_list.append(r)
        return jsonify({'status': 'success', 'data': history_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)