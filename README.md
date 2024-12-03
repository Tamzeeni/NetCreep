# NetCreep 🕸️🔍

## Network Monitoring and Analysis Toolkit

### Overview
NetCreep is an advanced, open-source network monitoring tool designed for comprehensive network traffic analysis, security monitoring, and performance tracking.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

### 🌟 Key Features
- Real-time network packet capture
- Multi-interface monitoring
- Advanced protocol analysis
- Anomaly detection
- Customizable alerting
- Web-based dashboard
- Secure authentication
- Performance metrics tracking

### 🚀 Quick Start

#### Prerequisites
- Python 3.9+
- Linux/macOS (recommended)
- Network interfaces for packet capture

#### Installation
```bash
# Clone the repository
git clone https://github.com/Tamzeeni/netcreep.git
cd netcreep

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser
```

### 🔧 Configuration
Customize your monitoring setup in `.env`:
```
# Network Interfaces
NETCREEP_CAPTURE_INTERFACES=eth0,lo

# Packet Filtering
NETCREEP_PACKET_FILTER=tcp port 80 or udp

# Security Settings
TWO_FACTOR_ENABLED=true
RATE_LIMIT_REQUESTS=100
```

### 🖥️ Running the Application
```bash
# Development Server
python manage.py runserver

# Production (Gunicorn)
gunicorn netcreep.wsgi:application
```

### 📊 Dashboard Features
- Real-time packet capture visualization
- Network traffic analysis
- Protocol distribution charts
- Top network talkers
- Anomaly detection alerts

### 🔒 Security
- Role-based access control
- Two-factor authentication
- Rate limiting
- IP whitelisting
- Secure packet processing

### 🧪 Testing
```bash
# Run tests
python -m pytest

# Code quality checks
flake8 .
black --check .
```

### 🤝 Contributing
See `CONTRIBUTING.md` for contribution guidelines.

### 📜 Ethical Use
NetCreep is designed for legitimate network monitoring. Always obtain proper consent and follow legal guidelines.

### 📦 Dependencies
- Django
- Scapy
- Channels
- Bootstrap
- psutil

### 📝 License
MIT License

### 🌐 Community
- Issues: [GitHub Issues](https://github.com/Tamzeeni/netcreep/issues)
- Discussions: [GitHub Discussions](https://github.com/Tamzeeni/netcreep/discussions)

### 🏆 Acknowledgments
- Open-source community
- Network security researchers
- Django and Python ecosystems

### 🔐 Configuration Guide

#### Environment Setup
1. Copy `.env.example` to `.env`
2. Fill in the required configuration values

#### Key Configuration Parameters
- `SECRET_KEY`: Generate a unique, secure secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Configure allowed host domains
- `DATABASE_URL`: Set up your PostgreSQL connection
- `EMAIL_*`: Configure SMTP settings for alerts
- `CAPTURE_INTERFACES`: Define network interfaces to monitor
- `SECURITY_*`: Set up CORS and CSRF protection
- `ALLOWED_IP_RANGES`: Whitelist IP ranges for access

#### Security Best Practices
- Never commit `.env` to version control
- Use strong, unique passwords
- Enable two-factor authentication
- Regularly rotate secrets and credentials
- Use environment-specific configurations

#### Sensitive Configuration Placeholders
Replace the following placeholders with your actual values:
- `REPLACE_WITH_STRONG_PASSWORD`: Use a complex, unique password
- `your-email@gmail.com`: Your monitoring email
- `your-app-specific-password`: App-specific SMTP password

#### Two-Factor Authentication
Enable two-factor authentication by setting `TWO_FACTOR_ENABLED=True`

#### Logging Configuration
- `LOGGING_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `LOGGING_FILE`: Specify log file path

#### Rate Limiting
Configure rate limiting to prevent abuse:
- `RATE_LIMIT_REQUESTS`: Maximum requests per period
- `RATE_LIMIT_PERIOD`: Time period in seconds
