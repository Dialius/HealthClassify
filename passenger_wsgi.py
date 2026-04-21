import os
import sys

# Tambahkan direktori aplikasi ke system path
sys.path.insert(0, os.path.dirname(__file__))

# Mengimpor instance Flask dari app.py Anda
# Pastikan di app.py variabelnya bernama "app" (misal: app = Flask(__name__))
from app import app as application
