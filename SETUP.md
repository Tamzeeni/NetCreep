# NetCreep Network Monitoring Tool - Setup Guide

## Prerequisites

### System Requirements
- Python 3.9+
- Linux/macOS (recommended)
- Minimum 4GB RAM
- Network interfaces for packet capture

### Required Tools
- Python
- pip
- virtualenv (recommended)
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/Tamzeeni/netcreep.git
cd netcreep
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy `.env.example` to `.env` and modify according to your environment:
```bash
cp .env.example .env
```

#### Key Configuration Parameters
- `SECRET_KEY`: Generate a unique, secure secret key
- `CAPTURE_INTERFACE`: Set your primary network interface
- `ALLOWED_HOSTS`: Configure allowed hosts
- `DATABASE_URL`: Set your database connection
- `LOGGING_FILE`: Set log file path

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Packet Capture Permissions
NetCreep requires root/sudo permissions for packet capture:
```bash
sudo setcap cap_net_raw,cap_net_admin=eip /path/to/python
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## Configuration Options

### Network Interfaces
Edit `NETCREEP_CAPTURE_INTERFACES` in `.env` to monitor multiple interfaces:
```
NETCREEP_CAPTURE_INTERFACES=eth0,lo,wlan0
```

### Packet Filtering
Customize packet capture with BPF filters:
```
NETCREEP_PACKET_FILTER=tcp port 80 or udp
```

### Security Settings
- Enable/disable two-factor authentication
- Configure rate limiting
- Set IP whitelisting

## Production Deployment

### Gunicorn with Nginx
```bash
gunicorn netcreep.wsgi:application
```

### Docker Deployment
```bash
docker-compose up --build
```

## Troubleshooting
- Ensure network capture permissions
- Check firewall settings
- Verify interface names
- Review log files

## Ethical Use Statement
NetCreep is designed for legitimate network monitoring.
Always obtain proper consent and follow legal guidelines.

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and contribution process.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
