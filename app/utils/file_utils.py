import os
import tempfile

def cleanup_temp_files():
    """Geçici dosyaları temizler"""
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.startswith('detected_plates_') and filename.endswith('.jpg'):
            try:
                os.remove(os.path.join(temp_dir, filename))
            except:
                pass
