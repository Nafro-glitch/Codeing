FROM python:3.9-slim

# تثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# تثبيت المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV SELENIUM_HEADLESS=1

# تشغيل البوت
CMD ["python", "enhanced_main.py"]
