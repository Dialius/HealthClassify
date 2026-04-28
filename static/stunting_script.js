document.addEventListener('DOMContentLoaded', () => {
    
    const stuntingForm = document.getElementById('stuntingForm');
    const initialState = document.getElementById('initialState');
    const loadingState = document.getElementById('loadingState');
    const resultArea = document.getElementById('resultArea');
    const statusBanner = document.getElementById('statusBanner');
    const statusIconBox = document.getElementById('statusIconBox');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    const resultStripe = document.getElementById('resultStripe');
    const aiRecommendationText = document.getElementById('aiRecommendationText');
    const reportId = document.getElementById('reportId');
    
    const btnSubmit = document.getElementById('btnSubmit');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');

    stuntingForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // --- ANIMASI LOADING DI BUTTON ---
        const originalBtnText = btnText.textContent;
        const originalBtnIcon = btnIcon.textContent;
        
        btnText.textContent = "Sedang Menganalisis dengan AI...";
        btnIcon.textContent = "hourglass_empty";
        btnIcon.classList.add("animate-spin");
        btnSubmit.disabled = true;

        // Mengambil data dari inputan
        const umur = document.getElementById('umur').value;
        const tinggi_badan = document.getElementById('tinggi').value;
        const genderRadio = document.querySelector('input[name="gender"]:checked');
        const jenis_kelamin = genderRadio ? genderRadio.value : "";

        // Show loading state, hide initials or previous results
        initialState.classList.add('hidden');
        resultArea.classList.add('hidden');
        loadingState.classList.remove('hidden');

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
                // Tampilkan Result Area dan sembunyikan loading/initial
                loadingState.classList.add('hidden');
                resultArea.classList.remove('hidden');

                // Generate report ID
                reportId.textContent = Math.floor(100000 + Math.random() * 900000);

                tampilkanHasilBalita(data.prediksi_gizi);
                
                // Render teks Saran AI menggunakan library Marked.js ke syntax HTML list
                if (typeof marked !== 'undefined') {
                    aiRecommendationText.innerHTML = marked.parse(data.ai_saran);
                } else {
                     // Fallback jika lib marked gagal diload
                    aiRecommendationText.innerText = data.ai_saran;
                }
                
                // Optional UI scroll smoothing (if on mobile, scrolls down)
                if (window.innerWidth < 1024) {
                    resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } else {
                alert("Error dari API: " + data.message);
            }
        })
        .catch(error => {
            console.error("Terjadi error:", error);
            
            // Revert views
            loadingState.classList.add('hidden');
            initialState.classList.remove('hidden');
            
            alert("Gagal menghubungi server. Pastikan Flask sedang berjalan.");
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
        const statusClean = status.toString().trim();
        statusText.textContent = statusClean;

        // Konfigurasi Warna Berdasarkan Status Gizi
        if (statusClean.includes('Sangat Stunting')) {
            statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-red-900/10 border-red-500/30 text-red-100";
            statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(239,68,68,0.3)] bg-red-500/20 border-red-500/50 z-10 text-red-400";
            resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] z-40";
            statusIcon.textContent = "warning";
            statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-red-400";
        } else if (statusClean.includes('Stunting')) {
            statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-orange-900/10 border-orange-500/30 text-orange-100";
            statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(249,115,22,0.3)] bg-orange-500/20 border-orange-500/50 z-10 text-orange-400";
            resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.8)] z-40";
            statusIcon.textContent = "error";
            statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-orange-400";
        } else if (statusClean.includes('Tinggi')) {
            statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-sky-900/10 border-sky-400/30 text-sky-100";
            statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(56,189,248,0.3)] bg-sky-400/20 border-sky-400/50 z-10 text-sky-400";
            resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-sky-400 shadow-[0_0_10px_rgba(56,189,248,0.8)] z-40";
            statusIcon.textContent = "trending_up";
            statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-sky-400";
        } else {
            statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-[#0f5132]/20 border-[#75b798]/30 text-emerald-100";
            statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(117,183,152,0.3)] bg-[#75b798]/20 border-[#75b798]/50 z-10 text-[#75b798]";
            resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-[#75b798] shadow-[0_0_10px_rgba(117,183,152,0.8)] z-40";
            statusIcon.textContent = "check_circle";
            statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-[#75b798]";
        }
    }
});
