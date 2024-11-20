# NetCreep - Network Monitoring Tool

## Overview
NetCreep is a real-time network monitoring and analysis tool built with Django. It provides system resource monitoring, packet sniffing, and network analysis capabilities through an intuitive web interface.

## Features
- **Real-time System Monitoring**
  - CPU usage tracking
  - Memory utilization
  - Disk usage monitoring
  - Network traffic analysis

- **Packet Sniffing**
  - Real-time packet capture
  - Protocol analysis
  - Traffic source/destination tracking
  - Last 1000 packets history (Can be adjusted)

- **Interactive Dashboard**
  - Real-time updates via WebSocket
  - Visual metrics representation
  - System resource graphs
  - Network activity feed

- **Anomaly Detection**
  - System resource anomalies
  - Network traffic spikes
  - Alert system

## Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (recommended) or SQLite
- Required Python packages:
```
django
channels
daphne
psutil
scapy
```

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/netcreep.git
cd netcreep
```

2. Create and activate a virtual environment:
```
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate
```

3. Install required packages:
```
pip install -r requirements.txt
```

4. Configure the database:
```
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```

## Running the Application

1. Start the Daphne server:
```
daphne netcreep.asgi:application
```

2. Access the application:
- Open your web browser and navigate to `http://localhost:8000`
- Admin interface is available at `http://localhost:8000/admin`

## Usage

### Dashboard
- View real-time system metrics
- Monitor network traffic
- Track resource utilization

### Packet Sniffing
1. Navigate to the packet sniffing control page
2. Click "Start Sniffing" to begin capturing packets
3. View captured packets in real-time
4. Click "Stop Sniffing" to end capture

### System Monitoring
- Real-time resource usage tracking
- Historical data viewing
- Anomaly detection and alerts

## Project Structure
```
netcreep/
├── manage.py
├── netcreep/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── monitor/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── sniffer.py
│   ├── system_monitor.py
│   ├── urls.py
│   └── views.py
└── templates/
    └── monitor/
        ├── dashboard.html
        └── other templates...
```

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=your-database-url
```

### Database Configuration
Default configuration uses SQLite. For PostgreSQL, update `settings.py`:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Security Considerations
- Run with appropriate permissions for packet capture
- Secure the admin interface
- Use HTTPS in production
- Regularly update dependencies
- Monitor system resource usage

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Django framework
- Channels for WebSocket support
- Scapy for packet capture
- psutil for system monitoring

## Support
For support, please open an issue in the GitHub repository or contact [your-email].

## Roadmap
- Enhanced network analysis
- Advanced alert system
- Historical data visualization
- Security features
- UI/UX improvements

## Authors
- Your Name - Initial work - [YourGitHub]

## Version History
- 0.1.0
  - Initial Release
  - Basic monitoring features
  - Real-time dashboard