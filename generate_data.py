import pandas as pd
import numpy as np
import os

np.random.seed(42)
num_samples = 10000

umur = np.random.randint(0, 37, num_samples)
jk_num = np.random.randint(0, 2, num_samples) # 0 Laki-laki, 1 Perempuan
jk_str = np.where(jk_num == 0, 'laki-laki', 'perempuan')

tinggi_badan = []
status_gizi = []

for u, jk in zip(umur, jk_num):
    if jk == 0:
        expected = 50 + (u * 1.3)
    else:
        expected = 49 + (u * 1.25)
    
    # Generate random height around expected (std dev 5)
    t = np.random.normal(expected, 6)
    
    # Clamp within limits (45 - 100 as per HTML)
    # Actually let's let some be taller to get "tinggi" and shorter to get "severely stunted"
    # But for realism, cap roughly around 40 to 110
    t = np.clip(t, 40, 110)
    tinggi_badan.append(round(t, 1))

    diff = t - expected
    if diff > 4:
        status_gizi.append('tinggi')
    elif diff >= -4:
        status_gizi.append('normal')
    elif diff >= -8:
        status_gizi.append('stunted')
    else:
        status_gizi.append('severely stunted')

df = pd.DataFrame({
    'Umur': umur,
    'Jenis Kelamin': jk_str,
    'Tinggi Badan': tinggi_badan,
    'Status Gizi': status_gizi
})

# Save to data/balita_fix.csv
os.makedirs('data', exist_ok=True)
df.to_csv('data/balita_fix.csv', index=False)
print("Generated data/balita_fix.csv with sensible logic.")
