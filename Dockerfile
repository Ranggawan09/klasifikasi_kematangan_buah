# Gunakan image Python terbaru
FROM python:3.12.9

# Set working directory
WORKDIR /app

# Copy semua file proyek ke dalam container
COPY . .

# Install dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
