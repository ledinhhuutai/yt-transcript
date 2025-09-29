# Hướng dẫn Deploy YouTube Transcript API

## Thông tin VPS
- **IP**: 222.255.119.5
- **Username**: root
- **Path**: /var/www/yt-transcript
- **Domain**: transcript.inonappstudio.com

## Bước 1: Upload files lên VPS

### Cách 1: Sử dụng SCP (từ Git Bash hoặc WSL)
```bash
# Upload tất cả files
scp -r * root@222.255.119.5:/var/www/yt-transcript/

# Hoặc upload từng file quan trọng
scp app_optimized.py root@222.255.119.5:/var/www/yt-transcript/
scp requirements_minimal.txt root@222.255.119.5:/var/www/yt-transcript/
scp -r yt_transcript/ root@222.255.119.5:/var/www/yt-transcript/
scp install_lightweight.sh root@222.255.119.5:/var/www/yt-transcript/
scp setup_subdomain.sh root@222.255.119.5:/var/www/yt-transcript/
scp nginx_subdomain_simple.conf root@222.255.119.5:/var/www/yt-transcript/
```

### Cách 2: Sử dụng WinSCP (GUI)
1. Mở WinSCP
2. Host: 222.255.119.5
3. Username: root
4. Password: cOBb;kAw=L{NyJI
5. Upload tất cả files vào /var/www/yt-transcript/

## Bước 2: SSH vào VPS và cài đặt

```bash
# Kết nối SSH
ssh root@222.255.119.5

# Di chuyển vào thư mục project
cd /var/www/yt-transcript

# Cấp quyền thực thi
chmod +x *.sh

# Cài đặt API
sudo ./install_lightweight.sh

# Cấu hình Nginx và SSL
sudo ./setup_subdomain.sh
```

## Bước 3: Kiểm tra service

```bash
# Kiểm tra service đang chạy
sudo systemctl status yt-transcript-lite

# Kiểm tra logs
sudo journalctl -u yt-transcript-lite -f

# Test API local
curl http://localhost:5001

# Test API qua domain
curl https://transcript.inonappstudio.com
```

## Bước 4: Test API

```bash
# Test transcript endpoint
curl "https://transcript.inonappstudio.com/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Troubleshooting

### Nếu service không chạy:
```bash
sudo systemctl restart yt-transcript-lite
sudo systemctl enable yt-transcript-lite
```

### Nếu Nginx lỗi:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Nếu SSL không hoạt động:
```bash
sudo certbot --nginx -d transcript.inonappstudio.com
```