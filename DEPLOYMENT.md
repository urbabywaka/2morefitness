# Deployment Guide for Render

This guide will help you deploy the 2moreFitness Django application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. A GitHub account
3. Your code pushed to a GitHub repository

## Deployment Steps

### Step 1: Push Your Code to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ready for deployment"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/2moreFitness.git

# Push to GitHub
git push -u origin main
```

### Step 2: Create a Render Account

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Deploy Using Blueprint (Recommended)

The easiest way is to use the `render.yaml` blueprint file included in this project.

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Click "Apply" to create all services

This will create:
- A web service running your Django app
- A PostgreSQL database

### Step 4: Configure Environment Variables (Manual Method)

If you prefer manual setup instead of blueprint:

1. **Create PostgreSQL Database:**
   - Click "New +" → "PostgreSQL"
   - Name: `2morefitness-db`
   - Choose Free plan (or higher)
   - Click "Create Database"
   - Copy the "Internal Database URL"

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `2morefitness`
     - **Region:** Choose closest to your users
     - **Branch:** `main`
     - **Root Directory:** Leave blank
     - **Runtime:** Python 3
     - **Build Command:** `./build.sh`
     - **Start Command:** `gunicorn gym_project.wsgi:application`
     - **Plan:** Free (or higher for production)

3. **Add Environment Variables:**
   Click "Environment" and add:
   
   ```
   SECRET_KEY=<generate-a-random-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=<paste-internal-database-url-here>
   STATIC_ADMIN_USERNAME=gymadmin
   STATIC_ADMIN_PASSWORD=<create-secure-password>
   TIME_ZONE=Asia/Manila
   ```

### Step 5: Generate SECRET_KEY

Generate a secure secret key using Python:

```python
# Run this in Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use this one-liner:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Step 6: Deploy

1. Click "Create Web Service" (or "Apply Blueprint")
2. Render will automatically:
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start your application

3. Wait for deployment to complete (5-10 minutes)

### Step 7: Create Superuser

After deployment:

1. Go to your Render Dashboard
2. Click on your web service
3. Click "Shell" tab
4. Run:
   ```bash
   python manage.py createsuperuser
   ```
5. Follow prompts to create admin account

### Step 8: Access Your Application

Your app will be available at:
```
https://2morefitness.onrender.com
```

Admin panel:
```
https://2morefitness.onrender.com/admin/
```

## Important Notes

### Free Tier Limitations

The free tier on Render:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~1 minute
- Database limited to 1GB
- 750 hours/month free

For production, consider:
- Upgrading to Starter plan ($7/month for web service)
- Upgrading database to Starter ($7/month)

### Custom Domain

To use your own domain:

1. Go to your web service settings
2. Click "Settings" → "Custom Domain"
3. Add your domain
4. Update DNS records as instructed
5. Update `ALLOWED_HOSTS` environment variable to include your domain

### Static Files

Static files are served using WhiteNoise, which is configured in the project.
No additional configuration needed.

### Media Files

For user uploads (photos, documents):
- Free tier: Files stored on disk (lost on redeployment)
- Production: Use AWS S3 or Cloudinary

To add S3 support:
1. Install `django-storages` and `boto3`
2. Configure in settings.py
3. Update environment variables

### Database Backups

1. Go to your database in Render Dashboard
2. Click "Backups"
3. Enable automatic backups

### Monitoring

Render provides:
- Logs: View application logs in real-time
- Metrics: CPU, Memory usage
- Alerts: Set up email notifications

## Troubleshooting

### Build Fails

Check build logs:
1. Click on your service
2. Go to "Events" tab
3. Click on failed build
4. Review error messages

Common issues:
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Build script errors

### Application Won't Start

Check logs:
1. Go to "Logs" tab
2. Look for error messages

Common issues:
- `DATABASE_URL` not set
- `SECRET_KEY` not set
- `ALLOWED_HOSTS` incorrect

### Static Files Not Loading

1. Check if `collectstatic` ran in build logs
2. Verify WhiteNoise is in `MIDDLEWARE`
3. Check `STATIC_ROOT` path

### Database Connection Issues

1. Verify `DATABASE_URL` is set correctly
2. Check database is running
3. Verify firewall rules (if custom database)

## Updating Your Application

To deploy updates:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Render automatically redeploys on push

To disable auto-deploy:
1. Go to service settings
2. Click "Auto-Deploy" → Disable

## Security Checklist

Before going live:

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] Database backups enabled
- [ ] Strong passwords for admin accounts
- [ ] HTTPS enabled (automatic on Render)
- [ ] Environment variables secured
- [ ] Remove default/test credentials

## Performance Optimization

For better performance:

1. **Enable Caching:**
   - Add Redis instance
   - Configure Django caching

2. **Database Optimization:**
   - Add database indexes
   - Use database connection pooling
   - Regular VACUUM on PostgreSQL

3. **Upgrade Plans:**
   - Starter plan for faster performance
   - More RAM/CPU for heavy usage

## Support

- Render Documentation: https://render.com/docs
- Django Documentation: https://docs.djangoproject.com/
- Project Issues: Check your GitHub repository

## Cost Estimation

### Free Tier
- Web Service: Free (with limitations)
- PostgreSQL: Free (1GB limit)
- **Total: $0/month**

### Production (Recommended)
- Web Service Starter: $7/month
- PostgreSQL Starter: $7/month
- **Total: $14/month**

### High Traffic
- Web Service Standard: $25/month
- PostgreSQL Standard: $25/month
- **Total: $50/month**

## Next Steps

After deployment:

1. Set up custom domain
2. Configure email service (SendGrid, Mailgun)
3. Set up monitoring and alerts
4. Configure backup strategy
5. Add SSL/TLS certificate (automatic on Render)
6. Set up CI/CD pipeline
7. Load test your application

## Additional Resources

- [Render Django Guide](https://render.com/docs/deploy-django)
- [Django Production Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PostgreSQL on Render](https://render.com/docs/databases)
