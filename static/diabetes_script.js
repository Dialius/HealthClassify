document.addEventListener('DOMContentLoaded', () => {
    
    // --- Custom Dropdown Logic ---
    const dropdownWrappers = document.querySelectorAll('.dropdown-wrapper');
    
    // Close all dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown-wrapper')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => menu.classList.remove('open'));
            document.querySelectorAll('.dropdown-arrow').forEach(arrow => arrow.classList.remove('open'));
        }
    });

    dropdownWrappers.forEach(wrapper => {
        const trigger = wrapper.querySelector('.select-trigger');
        const menu = wrapper.querySelector('.dropdown-menu');
        const arrow = wrapper.querySelector('.dropdown-arrow');
        const textDisplay = wrapper.querySelector('.selected-text');
        const hiddenInput = wrapper.querySelector('input[type="hidden"]');
        const options = menu.querySelectorAll('.option-item');

        // Toggle dropdown open/close
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close others first
            document.querySelectorAll('.dropdown-menu').forEach(m => {
                if(m !== menu) m.classList.remove('open');
            });
            document.querySelectorAll('.dropdown-arrow').forEach(a => {
                if(a !== arrow) a.classList.remove('open');
            });
            
            menu.classList.toggle('open');
            arrow.classList.toggle('open');
        });

        // Handle option selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Set text and value
                textDisplay.textContent = option.textContent;
                textDisplay.classList.remove('text-outline');
                textDisplay.classList.add('text-white');
                hiddenInput.value = option.getAttribute('data-value');
                
                // Close menu
                menu.classList.remove('open');
                arrow.classList.remove('open');
            });
        });
    });

    // --- Form Submission Logic ---
    const form = document.getElementById('diabetesForm');
    const resultArea = document.getElementById('resultArea');
    const initialState = document.getElementById('initialState');
    const loadingState = document.getElementById('loadingState');
    const statusBanner = document.getElementById('statusBanner');
    const statusIconBox = document.getElementById('statusIconBox');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    const resultStripe = document.getElementById('resultStripe');
    const aiRecommendationText = document.getElementById('aiRecommendationText');
    const reportId = document.getElementById('reportId');
    const btnSubmit = document.getElementById('btnSubmit');
    const btnIcon = document.getElementById('btnIcon');
    const btnText = document.getElementById('btnText');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validation check for hidden inputs
        const requiredInputs = form.querySelectorAll('input[type="hidden"][required]');
        for (let input of requiredInputs) {
            if (!input.value) {
                alert('Silakan pilih semua opsi dropdown sebelum menganalisis.');
                return;
            }
        }
        
        // Change button state
        btnSubmit.disabled = true;
        btnIcon.textContent = 'hourglass_empty';
        btnIcon.classList.add('animate-spin');
        btnText.textContent = 'Menganalisis...';
        
        // Prepare data
        const data = {
            gender: document.getElementById('gender').value,
            age: document.getElementById('age').value,
            hypertension: document.getElementById('hypertension').value,
            heart_disease: document.getElementById('heart_disease').value,
            smoking_history: document.getElementById('smoking_history').value,
            bmi: document.getElementById('bmi').value,
            HbA1c_level: document.getElementById('hba1c_level').value,
            blood_glucose_level: document.getElementById('blood_glucose_level').value
        };

        // Show loading state, hide initials or previous results
        initialState.classList.add('hidden');
        resultArea.classList.add('hidden');
        loadingState.classList.remove('hidden');

        try {
            const response = await fetch('/predict_diabetes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const result = await response.json();
            
            // Hide loading, Show result area
            loadingState.classList.add('hidden');
            resultArea.classList.remove('hidden');

            // Generate report ID
            reportId.textContent = Math.floor(100000 + Math.random() * 900000);

            // Apply classes and text based on prediction outcome
            if (result.prediction === "Positif Diabetes") {
                statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-red-900/10 border-red-500/30 text-red-100";
                statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(239,68,68,0.3)] bg-red-500/20 border-red-500/50 z-10 text-red-400";
                resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)] z-40";
                statusIcon.textContent = "warning";
                statusText.textContent = "Positif Diabetes";
                statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-red-400";
            } else {
                statusBanner.className = "relative overflow-hidden rounded-2xl border p-6 flex items-center gap-5 shadow-sm transition-all duration-500 bg-[#0f5132]/20 border-[#75b798]/30 text-emerald-100";
                statusIconBox.className = "w-16 h-16 rounded-full flex items-center justify-center shrink-0 border-2 shadow-[0_0_15px_rgba(117,183,152,0.3)] bg-[#75b798]/20 border-[#75b798]/50 z-10 text-[#75b798]";
                resultStripe.className = "absolute top-0 left-0 w-full h-[3px] bg-[#75b798] shadow-[0_0_10px_rgba(117,183,152,0.8)] z-40";
                statusIcon.textContent = "check_circle";
                statusText.textContent = "Negatif Diabetes";
                statusText.className = "text-2xl md:text-3xl font-black font-headline tracking-tighter text-[#75b798]";
            }

            // Render Markdown from AI
            aiRecommendationText.innerHTML = marked.parse(result.recommendation);

        } catch (error) {
            console.error('Error:', error);
            
            // Revert views
            loadingState.classList.add('hidden');
            initialState.classList.remove('hidden');
            
            alert('Terjadi kesalahan saat menganalisis. Silakan cek koneksi/console.');
        } finally {
            // Restore button state
            btnSubmit.disabled = false;
            btnIcon.classList.remove('animate-spin');
            btnIcon.textContent = 'biotech';
            btnText.textContent = 'Analisis Risiko Diabetes';
        }
    });
});
