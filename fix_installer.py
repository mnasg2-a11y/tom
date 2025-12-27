# أنشئ ملف fix.py جديد
cat > fix.py << 'EOF'
import subprocess
import sys

# قائمة بالإصلاحات
fixes = [
    "pip install setuptools<81 -q",
    "pip install pytz -q", 
    "pip install tzlocal -q",
    "pip install APScheduler==3.10.4 -q"
]

for fix in fixes:
    subprocess.run(fix, shell=True)

print("All fixes applied successfully")
print("Now run: python installer.py")
EOF

# شغله
python fix.py
