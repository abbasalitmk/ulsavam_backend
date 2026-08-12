# PostgreSQL Setup Guide for Ulsavam Backend

## Problem
SQLite database doesn't work well on Render because:
- Render doesn't have persistent file storage
- Each deployment wipes the database
- No way to keep data between deployments

## Solution: Use PostgreSQL on Render

### Step 1: Create a PostgreSQL Database on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"+ New"** → **"PostgreSQL"**
3. Fill in the details:
   - **Name**: `ulsavam-db` (or any name you prefer)
   - **Database**: Keep default `postgres`
   - **User**: Keep default `postgres` (or set custom)
   - **Region**: Choose same as your web service (Singapore)
   - **PostgreSQL Version**: 15 (latest)
   - **Plan**: Free tier (upgraded later if needed)
4. Click **"Create Database"**
5. Wait 2-3 minutes for the database to be created

### Step 2: Get the Database URL

1. Once created, you'll see your database in the dashboard
2. Look for the **"Internal Database URL"** - copy this
3. It looks like: `postgresql://user:password@host:5432/postgres`

### Step 3: Add DATABASE_URL to Your Web Service

1. Go to your **ulsavam_backend** web service
2. Click **"Environment"** in the left sidebar
3. Click **"+ Add Environment Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the internal database URL from Step 2
5. Click **"Save"**

### Step 4: Deploy Your App

1. Your Django app already supports PostgreSQL!
2. Go back to your web service dashboard
3. Click **"Manual Deploy"** to trigger a new deployment
4. The deployment will:
   - Install psycopg2 (PostgreSQL driver)
   - Run migrations to create tables
   - **Automatically seed data** with Kerala events and users

### Step 5: Verify It Works

Once deployed, you can:

**Check the database:**
```bash
# From Render dashboard, open PostgreSQL database
# Click "Connect" and use the connection details
```

**Test API endpoints:**
```bash
curl https://ulsavam-backend.onrender.com/api/districts/
curl https://ulsavam-backend.onrender.com/api/events/
```

## Using PostgreSQL Locally

If you want to use the same PostgreSQL database locally while developing:

### Option 1: Use Render's PostgreSQL Locally (Cloud Database)

1. Copy the **"External Database URL"** from Render PostgreSQL
2. It uses port 5432 and is accessible from anywhere
3. Set it locally:
```bash
export DATABASE_URL="postgresql://user:password@host.render.com:5432/postgres"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

⚠️ **Note**: The External URL is slower due to cloud latency. Only use for testing.

### Option 2: Use Local PostgreSQL (Recommended)

Install PostgreSQL locally:

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

Create local database:
```bash
createdb ulsavam_dev
```

Set Django to use it:
```bash
export DATABASE_URL="postgresql://localhost/ulsavam_dev"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Option 3: Docker PostgreSQL (Easiest)

```bash
# Start PostgreSQL in Docker
docker run --name ulsavam-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ulsavam_dev \
  -p 5432:5432 \
  -d postgres:15

# Set Django to use it
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ulsavam_dev"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Seed Data

The seed data includes:

✅ **13 Kerala Districts** with all districts properly named and slugified

✅ **6 Sample Users** including an admin account
- Admin: admin@ulsavam.com / password: admin123
- Regular users from different districts

✅ **18 Real Kerala Events** including:
- Thrissur Pooram Festival (temple)
- Cochin Carnivale (arts & culture)
- Attukal Pongala (temple - world's largest women gathering)
- Alleppey Food Festival (food)
- Wayanad Adventure Sports (sports)
- DJ Nights & Beach Meetups (dj_music, beach_meetup)
- Community gatherings, book festivals, and more

All events are:
- Marked as **verified** (ready to display)
- Set as **featured** (appears in top listings)
- Scheduled for various dates over next 60 days
- Have realistic Kerala locations with coordinates
- Organized by admin user

### To Reseed Data

If you want to clear and reseed:

**Locally:**
```bash
# Clear everything (careful!)
python manage.py flush --noinput

# Reseed
python manage.py seed_data
```

**On Render:**
You can't directly access the shell, but you can:
1. Delete and recreate the PostgreSQL database on Render
2. Or modify seed_data.py to check if data exists first (already does!)

## Troubleshooting

### "psycopg2: command not found"
- Make sure `psycopg2-binary==2.9.9` is in requirements.txt ✅ (Already added)
- Commit and deploy

### "FATAL: remaining connection slots are reserved"
- Free tier PostgreSQL allows limited connections
- Upgrade plan or close unused connections

### Database URL format issues
- Should start with `postgresql://`
- Include username:password
- Format: `postgresql://user:password@host:port/database`

### Data not seeding
- The seed_data command is idempotent (won't duplicate)
- Check logs on Render dashboard for errors
- Manually run: `python manage.py seed_data` if needed

## Next Steps

1. ✅ Create PostgreSQL database on Render
2. ✅ Add DATABASE_URL environment variable
3. ✅ Deploy your web service
4. ✅ Verify data is seeded
5. Test API endpoints
6. Build your frontend!

Happy building! 🚀
