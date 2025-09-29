#!/bin/bash

# Script cấu hình subdomain transcript.note.inonappstudio.com
# Sử dụng: bash setup_subdomain.sh

DOMAIN="transcript.note.inonappstudio.com"
MAIN_DOMAIN="note.inonappstudio.com"

echo "=== Cấu hình subdomain $DOMAIN ==="

# Kiểm tra Nginx đã cài đặt chưa
if ! command -v nginx &> /dev/null; then
    echo "Cài đặt Nginx..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y nginx
    elif command -v yum &> /dev/null; then
        sudo yum install -y nginx
    fi
fi

# Kiểm tra Certbot đã cài đặt chưa
if ! command -v certbot &> /dev/null; then
    echo "Cài đặt Certbot..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        sudo yum install -y certbot python3-certbot-nginx
    fi
fi

# Copy cấu hình Nginx
echo "Cấu hình Nginx cho $DOMAIN..."
sudo cp nginx_subdomain.conf /etc/nginx/sites-available/$DOMAIN

# Tạo symbolic link
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test cấu hình Nginx
echo "Kiểm tra cấu hình Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "Cấu hình Nginx hợp lệ. Reload Nginx..."
    sudo systemctl reload nginx
else
    echo "Lỗi cấu hình Nginx. Vui lòng kiểm tra lại."
    exit 1
fi

# Hướng dẫn cấu hình DNS
echo ""
echo "=== HƯỚNG DẪN CẤU HÌNH DNS ==="
echo "Bạn cần thêm DNS record sau vào domain $MAIN_DOMAIN:"
echo ""
echo "Type: A"
echo "Name: transcript"
echo "Value: $(curl -s ifconfig.me)"
echo "TTL: 300 (hoặc Auto)"
echo ""
echo "Hoặc nếu dùng Cloudflare/DNS provider khác:"
echo "transcript.note.inonappstudio.com -> $(curl -s ifconfig.me)"
echo ""

# Chờ user cấu hình DNS
read -p "Đã cấu hình DNS xong? Nhấn Enter để tiếp tục hoặc Ctrl+C để thoát..."

# Kiểm tra DNS đã propagate chưa
echo "Kiểm tra DNS propagation..."
if nslookup $DOMAIN | grep -q "$(curl -s ifconfig.me)"; then
    echo "DNS đã được cấu hình đúng!"
else
    echo "DNS chưa propagate hoặc cấu hình sai. Vui lòng đợi thêm hoặc kiểm tra lại."
    echo "Bạn có thể tiếp tục cài SSL sau khi DNS propagate."
    exit 0
fi

# Cài đặt SSL certificate
echo "Cài đặt SSL certificate cho $DOMAIN..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$MAIN_DOMAIN

if [ $? -eq 0 ]; then
    echo "SSL certificate đã được cài đặt thành công!"
else
    echo "Lỗi khi cài đặt SSL. Có thể DNS chưa propagate hoàn toàn."
    echo "Bạn có thể chạy lại lệnh sau khi DNS propagate:"
    echo "sudo certbot --nginx -d $DOMAIN"
fi

# Test cấu hình cuối cùng
echo ""
echo "=== KIỂM TRA CUỐI CÙNG ==="
echo "Test HTTP redirect:"
curl -I http://$DOMAIN

echo ""
echo "Test HTTPS:"
curl -I https://$DOMAIN

echo ""
echo "=== HOÀN TẤT ==="
echo "API có thể truy cập tại: https://$DOMAIN"
echo "Ví dụ: https://$DOMAIN/transcript?url=https://www.youtube.com/watch?v=VIDEO_ID"
echo ""
echo "Cập nhật Laravel config:"
echo "YOUTUBE_TRANSCRIPT_API_URL=https://$DOMAIN"