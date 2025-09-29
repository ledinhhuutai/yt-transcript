#!/bin/bash

# Script sửa lỗi Nginx config trực tiếp trên VPS
# Chạy: sudo bash fix_nginx_manual.sh

DOMAIN="transcript.inonappstudio.com"

echo "=== Sửa lỗi Nginx configuration ==="

# Xóa config cũ nếu có
sudo rm -f /etc/nginx/sites-enabled/transcript.note.inonappstudio.com
sudo rm -f /etc/nginx/sites-available/transcript.note.inonappstudio.com
sudo rm -f /etc/nginx/sites-enabled/transcript.inonappstudio.com
sudo rm -f /etc/nginx/sites-available/transcript.inonappstudio.com

echo "Tạo Nginx config mới..."

# Tạo config đơn giản không có rate limiting
sudo tee /etc/nginx/sites-available/transcript.inonappstudio.com > /dev/null <<EOF
server {
    listen 80;
    server_name transcript.inonappstudio.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name transcript.inonappstudio.com;

    # SSL Configuration (sẽ được cấu hình bởi Certbot)
    ssl_certificate /etc/letsencrypt/live/transcript.inonappstudio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/transcript.inonappstudio.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # API endpoint
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization" always;
        
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Logs
    access_log /var/log/nginx/transcript.inonappstudio.com.access.log;
    error_log /var/log/nginx/transcript.inonappstudio.com.error.log;
}
EOF

# Tạo symbolic link
sudo ln -s /etc/nginx/sites-available/transcript.inonappstudio.com /etc/nginx/sites-enabled/

# Test Nginx config
echo "Kiểm tra cấu hình Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx config OK!"
    
    # Reload Nginx
    sudo systemctl reload nginx
    echo "✅ Nginx đã được reload!"
    
    # Cài đặt SSL certificate
    echo "Cài đặt SSL certificate..."
    sudo certbot --nginx -d transcript.inonappstudio.com --non-interactive --agree-tos --email admin@inonappstudio.com
    
    echo "=== Hoàn thành! ==="
    echo "API có thể truy cập tại: https://transcript.inonappstudio.com"
    
else
    echo "❌ Nginx config có lỗi!"
    exit 1
fi