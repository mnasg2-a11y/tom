import os
import sys
import subprocess

print("🔧 جـاري إصـلاح الـمـشـاكـل الـنـهـائـي...")

# 1. إصلاح مشكلة timezone
os.environ['TZ'] = 'UTC'

# 2. تحديث setuptools لحل مشكلة pkg_resources
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools<81"])

# 3. إزالة وإعادة تثبيت apscheduler بإصدار متوافق
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "apscheduler"])
subprocess.run([sys.executable, "-m", "pip", "install", "apscheduler==3.10.4"])

# 4. تثبيت pytz للتأكد
subprocess.run([sys.executable, "-m", "pip", "install", "pytz"])

print("✅ تـم الإصـلاح بـنـجـاح!")
print("✨ الـآن شـغّـل مـلـف installer.py بـدون مـشـاكـل")
