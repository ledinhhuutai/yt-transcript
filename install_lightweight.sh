#!/bin/bash

# Script cài đặt YouTube Transcript API tối ưu cho VPS low-resource
# Sử dụng: sudo bash install_lightweight.sh

PROJECT_DIR="/var/www/yt-transcript"

echo "=== Cài đặt YouTube Transcript API cho VPS yếu ==="

# Kiểm tra RAM
echo "Kiểm tra tài nguyên hệ thống..."
free -h
df -h

# Cài đặt Python minimal
echo "Cài đặt Python và pip (minimal)..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y python3-minimal python3-pip python3-venv --no-install-recommends
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y python3 python3-pip
fi

# Tạo thư mục dự án
echo "Tạo thư mục dự án..."
sudo mkdir -p /opt/yt-transcript
sudo chown $USER:$USER /opt/yt-transcript
cd /opt/yt-transcript

# Tạo virtual environment nhẹ
echo "Tạo virtual environment..."
python3 -m venv venv --without-pip
source venv/bin/activate

# Cài đặt pip trong venv
curl https://bootstrap.pypa.io/get-pip.py | python

# Cài đặt dependencies tối thiểu
echo "Cài đặt dependencies tối thiểu..."
pip install --no-cache-dir -r requirements_minimal.txt

# Tạo systemd service tối ưu
echo "Tạo systemd service..."
sudo tee /etc/systemd/system/yt-transcript-lite.service > /dev/null <<EOF
[Unit]
Description=YouTube Transcript API (Lightweight)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/yt-transcript
Environment=PATH=/opt/yt-transcript/venv/bin
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/yt-transcript/venv/bin/python app_optimized.py
Restart=on-failure
RestartSec=30
MemoryLimit=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF

# Kích hoạt service
sudo systemctl daemon-reload
sudo systemctl enable yt-transcript-lite

echo "=== Cài đặt hoàn tất ==="
echo "Để khởi động service: sudo systemctl start yt-transcript-lite"
echo "Để kiểm tra trạng thái: sudo systemctl status yt-transcript-lite"
echo "API sẽ chạy tại: http://your-server-ip:5001"