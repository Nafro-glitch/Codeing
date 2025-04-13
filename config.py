import os

# توكن البوت - يتم قراءته من متغيرات البيئة في Railway
BOT_TOKEN = "7345445485:AAF2TOXdfANRLk3wGnXYQKVgs-UL40EAplg"

# معرف المسؤول - يتم قراءته من متغيرات البيئة في Railway
ADMIN_ID = 5584231309

# عدد المتصفحات المتزامنة - يتم قراءته من متغيرات البيئة في Railway
MAX_CONCURRENT_BROWSERS = 2

# مسار قاعدة البيانات
DATABASE_PATH = "database.db"

# إعدادات لوحة تحكم المسؤول
ADMIN_DASHBOARD_PORT = 5000
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# قراءة متغيرات البيئة إذا كانت متوفرة
if os.environ.get('BOT_TOKEN'):
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
if os.environ.get('ADMIN_ID'):
    ADMIN_ID = int(os.environ.get('ADMIN_ID'))
if os.environ.get('MAX_CONCURRENT_BROWSERS'):
    MAX_CONCURRENT_BROWSERS = int(os.environ.get('MAX_CONCURRENT_BROWSERS'))
if os.environ.get('RAILWAY_STATIC_URL'):
    ADMIN_DASHBOARD_URL = os.environ.get('RAILWAY_STATIC_URL').rstrip('/') + '/admin'
