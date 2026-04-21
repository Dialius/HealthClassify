document.addEventListener('DOMContentLoaded', () => {
    
    const stuntingForm = document.getElementById('stuntingForm');
    const resultArea = document.getElementById('resultArea');
    const btnSubmit = document.getElementById('btnSubmit');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');
    
    const statusBadge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');
    const statusIcon = document.getElementById('statusIcon');
    const aiRecommendationText = document.getElementById('aiRecommendationText');

    stuntingForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // --- ANIMASI LOADING DI BUTTON ---
        const originalBtnText = btnText.textContent;
        const originalBtnIcon = btnIcon.textContent;
        
        btnText.textContent = "Sedang Menganalisis dengan AI...";
        btnIcon.textContent = "hourglass_empty"; // Material icon
        btnIcon.classList.add("animate-spin"); // Efek muter-muter
        btnSubmit.disabled = true;

        // Tampilkan area skeleton / abu-abu sebelum hasil datang
        resultArea.classList.remove('hidden');
        statusBadge.className = 'inline-flex items-center gap-3 bg-gray-200 px-6 py-3 rounded-full shadow-sm transition-all duration-500';
        statusText.textContent = 'Menganalisis...';
        statusText.className = 'text-xl font-extrabold text-gray-500 font-headline tracking-tight';
        statusIcon.textContent = 'hourglass_bottom';
        statusIcon.className = 'material-symbols-outlined text-gray-500 text-2xl';
        
        aiRecommendationText.innerHTML = '<span class="animate-pulse">Menghubungi AI untuk rekomendasi penanganan terbaik...</span>';

        // Mengambil data dari inputan
        const umur = document.getElementById('umur').value;
        const tinggi_badan = document.getElementById('tinggi').value;
        // Mendapatkan radio button yang dipilih (Laki-laki = 0, Perempuan = 1)
        const genderRadio = document.querySelector('input[name="gender"]:checked');
        const jenis_kelamin = genderRadio ? genderRadio.value : "";

        // --- FETCH API KE BACKEND FLASK ---
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'umur': umur,
                'jenis_kelamin': jenis_kelamin,
                'tinggi_badan': tinggi_badan
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Terjadi kesalahan pada server.");
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                tampilkanHasilBalita(data.prediksi_gizi);
                
                // Render teks Saran AI menggunakan library Marked.js ke syntax HTML list
                if (typeof marked !== 'undefined') {
                    // hapus class animate-pulse karena data sudah sampai
                    aiRecommendationText.innerHTML = marked.parse(data.ai_saran);
                } else {
                     // Fallback jika lib marked gagal diload
                    aiRecommendationText.innerText = data.ai_saran;
                }
                
                // Optional UI scroll smoothing
                resultArea.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else {
                alert("Error dari API: " + data.message);
                resultArea.classList.add('hidden');
            }
        })
        .catch(error => {
            console.error("Terjadi error:", error);
            alert("Gagal menghubungi server. Pastikan Flask sedang berjalan.");
            resultArea.classList.add('hidden');
        })
        .finally(() => {
            // Animasi Loading Berhenti
            btnText.textContent = originalBtnText;
            btnIcon.textContent = originalBtnIcon;
            btnIcon.classList.remove("animate-spin");
            btnSubmit.disabled = false;
        });
    });

    function tampilkanHasilBalita(status) {
        const statusClean = status.toString().trim().toUpperCase();
        statusText.textContent = `Status Gizi: ${statusClean}`;

        // Konfigurasi Warna Berdasarkan Status Gizi (Memanfaatkan palet warna Tailwind)
        if (statusClean.includes('TINGGI') || statusClean.includes('NORMAL')) {
            // Hijau - Aman
            statusBadge.className = 'inline-flex items-center gap-3 bg-[#e8f5e9] px-6 py-3 rounded-full shadow-sm transition-all duration-500';
            statusText.className = 'text-xl font-extrabold text-[#1b5e20] font-headline tracking-tight';
            statusIcon.className = 'material-symbols-outlined text-[#1b5e20] text-2xl animate-bounce';
            statusIcon.textContent = 'check_circle';
        } else if (statusClean.includes('SEVERELY')) {
            // Orange/Red - Perlu Perhatian Ekstra
            statusBadge.className = 'inline-flex items-center gap-3 bg-red-100 px-6 py-3 rounded-full shadow-sm transition-all duration-500';
            statusText.className = 'text-xl font-extrabold text-red-800 font-headline tracking-tight';
            statusIcon.className = 'material-symbols-outlined text-red-800 text-2xl';
            statusIcon.textContent = 'warning';
        } else {
            // Merah - Stunted dsb.
            statusBadge.className = 'inline-flex items-center gap-3 bg-rose-100 px-6 py-3 rounded-full shadow-sm transition-all duration-500';
            statusText.className = 'text-xl font-extrabold text-rose-800 font-headline tracking-tight';
            statusIcon.className = 'material-symbols-outlined text-rose-800 text-2xl animate-pulse';
            statusIcon.textContent = 'medical_services';
        }
    }
});
