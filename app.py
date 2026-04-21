from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import requests

app = Flask(__name__)

# Memuat model yang sudah dilatih
try:
    knn_model = joblib.load('models/model_knn.pkl')
    scaler = joblib.load('models/scaler.pkl')
    le_status = joblib.load('models/label_encoder.pkl')
except Exception as e:
    print(f"Error loading models. Make sure you have run scripts/train.py first. Error: {e}")

import os
from dotenv import load_dotenv

load_dotenv()

# Kunci API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def get_backup_recommendation(status_gizi):
    """Sistem Pakar Lokal sebagai backup terakhir jika semua API mati."""
    status = str(status_gizi).lower()
    if status == 'severely stunted':
        return ("* **Konsultasi Medis Segera:** Mari segera jadwalkan kunjungan ke Dokter Spesialis Anak untuk observasi komprehensif dan intervensi gizi medis khusus.\n"
                "* **Prioritaskan Asupan Protein Hewani:** Sangat disarankan memberikan sumber protein adekuat seperti telur, ikan, daging, atau susu formula khusus sesuai rekomendasi medis.\n"
                "* **Jaga Protokol Kebersihan:** Anak pada kondisi ini rentan terhadap infeksi. Mohon pastikan sterilisasi alat makannya dan terapkan kebersihan lingkungan.")
    elif status == 'stunted':
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
    
    Berikan edukasi medis serta maksimal 3 poin saran penanganan klinis dan pola asuh suportif untuk panduan orang tua. 
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
    
    Berikan edukasi medis serta maksimal 3 poin saran penanganan klinis dan pola asuh suportif untuk panduan orang tua. 
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

@app.route('/')
def home():
    # Menampilkan file HTML (Portal Pemilihan Form)
    return render_template('home.html')

@app.route('/stunting')
def stunting():
    # Menampilkan form stunting
    return render_template('index.html')

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
        
        # 3. Panggil AI untuk rekomendasi (Gemini -> Groq -> Lokal)
        jk_text = "Laki-laki" if jk == 0 else "Perempuan"
        ai_recomendation = get_gemini_recommendation(umur, jk_text, tinggi, prediction_label)
        
        return jsonify({
            'status': 'success',
            'prediksi_gizi': prediction_label,
            'ai_saran': ai_recomendation
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)