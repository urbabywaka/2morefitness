# 2moreFitness - Gym Membership Management System

A complete, production-ready gym membership management system built with Django, SQLite, and vanilla HTML/CSS/JavaScript.

## Features

### User Roles
- **Admin**: Full system management, reports, and analytics
- **Trainer**: Manage classes and view member progress
- **Member**: Book classes, track attendance, manage membership

### Core Modules
1. **Authentication System**
   - Secure login/logout
   - User registration
   - Role-based access control

2. **Member Management**
   - Member profiles
   - Membership plans and subscriptions
   - Payment tracking
   - Membership history

3. **Trainer Management**
   - Trainer profiles
   - Specializations and certifications
   - Class assignments

4. **Class Management**
   - Group fitness classes
   - Class schedules
   - Enrollment system
   - Capacity management

5. **Attendance Tracking**
   - Check-in/check-out system
   - Attendance history
   - Analytics and reports

6. **Dashboard System**
   - Role-specific dashboards
   - Real-time statistics
   - Quick actions

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Architecture**: Django MVT (Model-View-Template)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Extract the project**
```bash
unzip 2moreFitness.zip
cd 2moreFitness
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install django pillow
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser** (admin account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

6. **Load sample data** (optional)
```bash
python manage.py shell < setup_sample_data.py
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Public site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/login/

## Default Accounts

After running the superuser creation:
- **Admin**: Use the credentials you created during `createsuperuser`

To create test accounts:
1. Go to the admin panel
2. Create users with different roles (admin, trainer, member)

## Project Structure

```
2moreFitness/
├── apps/
│   ├── core/              # Core functionality, landing page
│   ├── members/           # Member management
│   ├── trainers/          # Trainer management
│   ├── classes/           # Class scheduling
│   └── attendance/        # Attendance tracking
├── gym_project/           # Django project settings
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── templates/            # HTML templates
├── media/                # Uploaded files
├── manage.py            # Django management script
└── README.md            # This file
```

## Usage Guide

### Admin Functions
1. Login to admin panel: http://127.0.0.1:8000/admin/
2. Manage:
   - User profiles and roles
   - Membership plans
   - Trainers
   - Classes
   - View reports

### Member Functions
1. Register account
2. Purchase membership
3. Browse and enroll in classes
4. Check-in/check-out
5. View attendance history

### Trainer Functions
1. Update trainer profile
2. View assigned classes
3. Manage class information

## Customization

### Branding
- Logo and colors are in `static/css/style.css` (CSS variables)
- Modify hero section text in `templates/core/index.html`

### Adding Features
1. Create new app: `python manage.py startapp app_name`
2. Add to `INSTALLED_APPS` in `gym_project/settings.py`
3. Create models, views, URLs
4. Run migrations

### Deployment

#### For Production

1. **Update settings** (`gym_project/settings.py`):
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secret-key-here'
```

2. **Collect static files**:
```bash
python manage.py collectstatic
```

3. **Use production database** (optional):
   - Consider PostgreSQL or MySQL for production
   - Update DATABASE settings accordingly

4. **Deploy** to:
   - PythonAnywhere
   - Heroku
   - DigitalOcean
   - AWS
   - Your own server with Gunicorn + Nginx

## Database Schema

### Core Models
- **UserProfile**: Extended user information with role management
- **MembershipPlan**: Available membership tiers
- **ContactMessage**: Contact form submissions

### Member Models
- **Member**: Gym member profile
- **Membership**: Member subscription records

### Trainer Models
- **Trainer**: Trainer profile and certifications

### Class Models
- **GymClass**: Group fitness classes

### Attendance Models
- **Attendance**: Check-in/check-out records

## API Endpoints

### Public Pages
- `/` - Landing page
- `/login/` - User login
- `/register/` - Member registration
- `/membership-plans/` - View all plans
- `/classes/` - Browse classes
- `/trainers/` - View trainers

### Member Pages (Login Required)
- `/dashboard/` - Role-based dashboard redirect
- `/members/profile/` - Member profile
- `/members/purchase/` - Purchase membership
- `/attendance/check-in/` - Check-in
- `/attendance/check-out/` - Check-out

### Admin Pages (Admin Only)
- `/admin-dashboard/` - Admin dashboard
- `/attendance/report/` - Attendance reports
- `/members/` - Member list

## Security Features

- CSRF protection enabled
- Password validation
- Role-based access control
- Secure session management
- XSS protection headers

## Support

For issues or questions:
1. Check Django documentation: https://docs.djangoproject.com/
2. Review error logs in console
3. Check database integrity

## License

This project is created for educational purposes.

## Credits

- Design inspiration: GoGym.ph
- Framework: Django
- Created: 2026
