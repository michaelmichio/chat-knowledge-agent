FROM python:3.12-slim

# Atur direktori kerja
WORKDIR /app

# Copy requirements lebih dulu agar cache build bisa dimanfaatkan
COPY requirements.txt .

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY . .

EXPOSE 8000

# Jalankan FastAPI pakai uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
