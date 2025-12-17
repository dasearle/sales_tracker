# Sales Tracker

A sales tracking application with Microsoft 365 SSO authentication and role-based access control.

## Architecture

- **Backend**: Supabase (database, auth, RLS policies)
- **Frontend**: Flask (Python web framework)
- **Authentication**: Microsoft 365 SSO via Supabase Auth
- **Deployment**: AWS Elastic Beanstalk

## Roles

| Role | Access |
|------|--------|
| Admin | Full access to all features + user management |
| Management | Full access to sales, marketing, and reports |
| Sales | Access to sales dashboard and own data |
| Marketing | Access to marketing dashboard and client data |

## Setup

### 1. Supabase Configuration

1. Create a Supabase project (via AWS Marketplace or supabase.com)
2. Run the SQL scripts in `docs/supabase_setup.sql` (see plan file)
3. Enable the Custom Access Token hook in Authentication > Hooks

### 2. Azure AD Configuration

1. Register an application in Microsoft Entra ID
2. Create a client secret
3. Add redirect URI: `https://<your-supabase-project>.supabase.co/auth/v1/callback`
4. Configure the Azure provider in Supabase Authentication settings

### 3. Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Edit .env with your Supabase and Azure credentials

# Run the application
python application.py
```

Visit http://localhost:5000

### 4. Bootstrap Admin User

After your first login, run this SQL in Supabase to make yourself an admin:

```sql
UPDATE public.user_roles 
SET role = 'admin' 
WHERE user_id = '<your-user-id>';
```

### 5. Deploy to Elastic Beanstalk

```bash
# Initialize EB
eb init -p python-3.11 sales-tracker

# Create environment
eb create sales-tracker-env

# Set environment variables
eb setenv FLASK_SECRET_KEY="..." SUPABASE_URL="..." SUPABASE_ANON_KEY="..." SUPABASE_SERVICE_ROLE_KEY="..." REDIRECT_BASE_URL="https://your-eb-url"
```

## Project Structure

```
sales_tracker/
├── application.py          # Elastic Beanstalk entry point
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── config.py           # Configuration
│   ├── auth/               # Authentication module
│   ├── admin/              # Admin module (user management)
│   ├── main/               # Main routes
│   └── templates/          # HTML templates
├── requirements.txt
├── .env.example
└── .ebextensions/          # EB configuration
```

## License

Proprietary
