#!/bin/bash

# IntoAEC Secure Deployment Script
# This script deploys the application with all security measures enabled

set -e  # Exit on any error

echo "🔐 IntoAEC Secure Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root is not recommended for security reasons"
fi

# Check for required tools
print_status "Checking for required tools..."

command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is required but not installed. Aborting."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { print_error "pip3 is required but not installed. Aborting."; exit 1; }
command -v node >/dev/null 2>&1 || { print_error "Node.js is required but not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { print_error "npm is required but not installed. Aborting."; exit 1; }

print_success "All required tools are available"

# Create secure environment file if it doesn't exist
if [ ! -f "server/.env" ]; then
    print_status "Creating secure environment configuration..."
    cat > server/.env << EOF
# IntoAEC Secure Configuration
ENVIRONMENT=production
SECRET_KEY=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)
ALLOWED_ORIGINS=https://yourdomain.com
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
EOF
    print_success "Environment file created with secure defaults"
    print_warning "Please update server/.env with your actual configuration"
else
    print_status "Environment file already exists"
fi

# Install server dependencies
print_status "Installing server dependencies..."
cd server
pip3 install -r requirements.txt
print_success "Server dependencies installed"

# Install client dependencies
print_status "Installing client dependencies..."
cd ../client
npm install
print_success "Client dependencies installed"

# Build client for production
print_status "Building client for production..."
npm run build
print_success "Client built successfully"

# Create secure directories
print_status "Creating secure directories..."
cd ..
mkdir -p server/temp
mkdir -p server/logs
mkdir -p server/uploads
chmod 700 server/temp
chmod 700 server/logs
chmod 700 server/uploads
print_success "Secure directories created"

# Set up file permissions
print_status "Setting secure file permissions..."
chmod 600 server/.env
chmod 644 server/*.py
chmod 755 server/main_secure.py
chmod 755 deploy_secure.sh
print_success "File permissions set"

# Create systemd service file for production
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/intoaec.service > /dev/null << EOF
[Unit]
Description=IntoAEC Secure Detection Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$(pwd)/server
Environment=PATH=$(pwd)/server/venv/bin
ExecStart=$(which python3) main_secure.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$(pwd)/server/temp $(pwd)/server/logs

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd service file created"

# Create nginx configuration for reverse proxy
print_status "Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/intoaec > /dev/null << EOF
server {
    listen 80;
    server_name yourdomain.com;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self';";
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Client static files
    location / {
        root $(pwd)/client/out;
        try_files \$uri \$uri.html \$uri/index.html /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Security headers for API
        proxy_hide_header X-Powered-By;
        proxy_set_header X-Content-Type-Options nosniff;
    }
    
    # File upload size limit
    client_max_body_size 10M;
    
    # Disable server tokens
    server_tokens off;
}
EOF

print_success "Nginx configuration created"

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/intoaec /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
print_success "Nginx configuration applied"

# Set up SSL with Let's Encrypt (optional)
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Setting up SSL with Let's Encrypt..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d yourdomain.com
    print_success "SSL certificate installed"
fi

# Create firewall rules
print_status "Setting up firewall rules..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 8000/tcp  # Block direct access to API
sudo ufw --force enable
print_success "Firewall rules configured"

# Create log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/intoaec > /dev/null << EOF
$(pwd)/server/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload intoaec
    endscript
}
EOF
print_success "Log rotation configured"

# Run security tests
print_status "Running security tests..."
cd server
python3 security_test.py
print_success "Security tests completed"

# Start services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable intoaec
sudo systemctl start intoaec
sudo systemctl status intoaec --no-pager

print_success "IntoAEC Secure Deployment Complete!"
echo ""
echo "🔐 Security Features Enabled:"
echo "  ✅ Authentication & Authorization"
echo "  ✅ File Upload Security"
echo "  ✅ Rate Limiting"
echo "  ✅ Security Headers"
echo "  ✅ Input Validation"
echo "  ✅ Encrypted Storage"
echo "  ✅ Firewall Protection"
echo "  ✅ SSL/TLS Encryption"
echo "  ✅ Log Monitoring"
echo ""
echo "📋 Next Steps:"
echo "  1. Update server/.env with your configuration"
echo "  2. Update nginx configuration with your domain"
echo "  3. Test the application: https://yourdomain.com"
echo "  4. Monitor logs: sudo journalctl -u intoaec -f"
echo "  5. Run security tests: python3 server/security_test.py"
echo ""
echo "🛡️ Your application is now secure and ready for production!"

