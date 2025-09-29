#!/bin/bash

# Script để upload các file cần thiết lên VPS
# Thông tin VPS đã được cấu hình

VPS_IP="222.255.119.5"
VPS_USER="root"
VPS_PATH="/var/www/yt-transcript"

echo "=== Upload YouTube Transcript API lên VPS ==="

# Tạo thư mục trên VPS
ssh $VPS_USER@$VPS_IP "mkdir -p $VPS_PATH"

# Upload các file chính
echo "Uploading main files..."
scp app.py $VPS_USER@$VPS_IP:$VPS_PATH/
scp app_optimized.py $VPS_USER@$VPS_IP:$VPS_PATH/
scp requirements.txt $VPS_USER@$VPS_IP:$VPS_PATH/
scp requirements_minimal.txt $VPS_USER@$VPS_IP:$VPS_PATH/
scp -r yt_transcript/ $VPS_USER@$VPS_IP:$VPS_PATH/

# Upload scripts
echo "Uploading setup scripts..."
scp install_lightweight.sh $VPS_USER@$VPS_IP:$VPS_PATH/
scp setup_subdomain.sh $VPS_USER@$VPS_IP:$VPS_PATH/

# Upload Nginx configs
echo "Uploading Nginx configs..."
scp nginx_subdomain.conf $VPS_USER@$VPS_IP:$VPS_PATH/
scp nginx_subdomain_simple.conf $VPS_USER@$VPS_IP:$VPS_PATH/

# Cấp quyền thực thi cho scripts
ssh $VPS_USER@$VPS_IP "chmod +x $VPS_PATH/*.sh"

echo "=== Upload hoàn tất! ==="
echo "Bây giờ hãy SSH vào VPS và chạy:"
echo "cd $VPS_PATH"
echo "sudo ./install_lightweight.sh"
echo "sudo ./setup_subdomain.sh"