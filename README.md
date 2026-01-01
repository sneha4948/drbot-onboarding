# DR Bot Patient Onboarding Web Form

## Overview
Django-based web application for registering patients into the DR Bot system for Diabetic Retinopathy screening at Sankara Eye Hospital.

## Features
- Patient information collection (Name, ID, Phone, DOB, Gender)
- Multi-language support (English, Hindi, Kannada, Tamil, Telugu)
- Doctor and staff assignment
- WhatsApp integration via DR Bot backend
- Azure App Service deployment ready

## Setup

### Local Development
```bash
cd myproject
pip install -r requirements.txt
python manage.py runserver
```

Visit: http://localhost:8000

### Configuration
Update `views.py` line 85 with your DR Bot backend URL:
- Local: `http://localhost:5000/register_users`
- Production: `https://your-drbot-backend.azurewebsites.net/register_users`

### Azure Deployment
1. Create Azure App Service (Python 3.10)
2. Configure environment variables:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
3. Deploy via GitHub Actions or Azure Deployment Center

## API Integration
Sends POST request to DR Bot backend `/register_users` endpoint with:
- Patient details
- Medical expert (doctor) assignment
- Logistical expert (staff) assignment
- Language preference
- Onboarding flag (triggers WhatsApp welcome flow)

## Tech Stack
- Django 5.2.6
- Python 3.10+
- Bootstrap 4.5.2
- Azure App Service

## License
Copyright © 2026 Sankara Eye Hospital
