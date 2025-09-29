#!/bin/bash

# Configuration
DOMAIN="transcript.inonappstudio.com"
PROJECT_DIR="/var/www/yt-transcript"

echo "🚀 Setting up HTTP-only Nginx configuration for $DOMAIN..."

# Remove old configurations
echo "📝 Removing old configurations..."
sudo rm -f /etc/nginx/sites-enabled/transcript.note.inonappstudio.com
sudo rm -f /etc/nginx/sites-available/transcript.note.inonappstudio.com
sudo rm -f /etc/nginx/sites-enabled/$DOMAIN
sudo rm -f /etc/nginx/sites-available/$DOMAIN

# Create new HTTP-only configuration
echo "📝 Creating HTTP-only Nginx configuration..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << 'EOF'
server {
    listen 80;
    server_name transcript.inonappstudio.com;

    # API endpoint
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization" always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "*";
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
            add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain charset=UTF-8";
            add_header Content-Length 0;
            return 204;
        }
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5001/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Logs
    access_log /var/log/nginx/transcript.inonappstudio.com.access.log;
    error_log /var/log/nginx/transcript.inonappstudio.com.error.log;
}
EOF

# Enable the site
echo "🔗 Enabling site..."
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "🧪 Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    # Reload Nginx
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo "✅ Setup completed successfully!"
    echo "🌐 Your API will be available at: http://$DOMAIN"
    echo ""
    echo "📋 Next steps:"
    echo "1. Make sure your Python API is running on port 5001"
    echo "2. Test the API: curl http://$DOMAIN/health"
    echo "3. Test transcript: curl 'http://$DOMAIN/transcript?url=YOUTUBE_URL'"
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi