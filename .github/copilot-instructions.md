# Copilot Instructions for blogapp

## Architecture Overview
This is a Flask-based blog application with MySQL database backend, designed for deployment on Google Cloud Platform. The app uses Flask-SQLAlchemy ORM with two main models: `Posts` (blog content) and `Contacts` (contact form submissions).

**Key architectural decision**: The `local_server` flag in `__init__.py` switches between local development (hardcoded MySQL connection) and production (config.json `prod_uri`). Currently defaults to local mode with GCP Cloud SQL socket path.

## Project Structure
- `blogapp/__init__.py` - Single-file Flask app containing all routes, models, and configuration
- `blogapp/config.json` - Database credentials and GCP project settings (NOT in .gitignore - contains sensitive data)
- `blogapp/template/` - Jinja2 templates using inheritance pattern (`layout.html` is base)
- `blogapp/static/` - Start Bootstrap "Clean Blog" theme assets

## Critical Workflows

### Initial Setup & Database Creation
```bash
# Install dependencies
pip install -r blogapp/requirements.txt

# Database initialization happens automatically via create_table() call at module level
# IMPORTANT: Comment out create_table() after first run to avoid recreation
```

**Warning**: The line `create_table()` at the bottom of `__init__.py` runs on every import. This is intentional for first-time setup but should be commented out afterward.

### Running the Application
```bash
cd blogapp
python __init__.py
# Runs on 0.0.0.0:80 (requires root/admin on most systems)
```

### GCP Deployment Setup
The app is configured for Google Cloud Platform with Cloud SQL:

1. **Cloud SQL Socket Path**: `/cloudsql/projectid:us-central1:codingthunder`
   - Replace `projectid` with actual GCP project ID from `config.json` (`axial-radius-337205`)
   - Format: `/cloudsql/{PROJECT_ID}:{REGION}:{INSTANCE_NAME}`

2. **Database Connection**: Uses `mysql+mysqldb://` driver with Unix socket connection
   - Public IP from config: `35.226.209.40:3306`
   - Update `__init__.py` line 15 with actual credentials and paths

3. **Config Params**: `config.json` contains:
   - `PROJECT_ID`: GCP project identifier
   - `INSTANCE_NAME`: Cloud SQL instance name
   - `PUBLIC_IP_ADDRESS`: External database IP
   - Both `dev_uri` and `prod_uri` currently point to localhost (needs updating for actual production)

**Security Note**: The current config has placeholder credentials. For production deployment, use GCP Secret Manager instead of `config.json`.

## Project-Specific Patterns

### Database Configuration
- MySQL connection uses `mysql+mysqldb://` driver (not `mysql+pymysql://`)
- Local mode uses Cloud SQL Unix socket path: `/cloudsql/projectid:us-central1:codingthunder`
- Production mode reads from `config.json` `prod_uri` (currently identical to dev_uri)
- The `local_server` boolean controls which URI is used, NOT environment detection

### Template Conventions
- All templates extend `layout.html` via `{%extends "layout.html" %}`
- Content goes in `{%block body %}` ... `{% endblock %}`
- Static assets use `url_for('static', filename='path/to/file')` pattern
- Navigation is hardcoded in `layout.html` - update there to change site-wide nav

### Route Patterns
- Blog posts use slug-based URLs: `/post/<string:post_slug>`
- Contact form uses POST method; other routes are GET-only
- The `params` variable from `config.json` is passed to templates but underutilized (only in `contact.html`)

### Authentication & Admin Workflows
**Current State**: No authentication system implemented. Critical gaps:

- **No Admin Interface**: Blog posts must be created directly via database/SQL queries
  - No route for creating, editing, or deleting posts
  - No admin login or session management
  - Consider adding Flask-Login or Flask-Admin for post management

- **Contact Form**: Accepts submissions without validation or spam protection
  - No CAPTCHA or rate limiting
  - No email notifications on new submissions
  - Contact entries stored but no admin view to read them

- **No User Management**: No user registration, login, or roles
  - All content is public-facing
  - No author attribution system beyond static templates

**To implement admin features**, you'll need to:
1. Add Flask-Login to `requirements.txt`
2. Create `User` model for authentication
3. Add `/admin/` routes with `@login_required` decorator
4. Create admin templates for CRUD operations on `Posts` and viewing `Contacts`

### Static vs Dynamic Content Issue
**Critical Pattern Mismatch**: `index.html` contains hardcoded blog post previews instead of dynamically loading from database:

```python
# index.html shows static HTML posts, but should query database:
# posts = Posts.query.order_by(Posts.date.desc()).all()
```

**Current Behavior**:
- Homepage displays 4 hardcoded "Start Bootstrap" sample posts
- These are NOT from the `Posts` table in the database
- Links point to `/post` (generic) instead of `/post/<slug>` with actual slugs
- Post dates and authors are hardcoded strings, not database fields

**To Fix**: Update `home()` route in `__init__.py`:
```python
@app.route("/")
def home():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    return render_template('index.html', posts=posts)
```

Then update `index.html` to loop over `posts` with Jinja2 syntax:
```jinja
{% for post in posts %}
<div class="post-preview">
    <a href="/post/{{ post.slug }}">
        <h2 class="post-title">{{ post.title }}</h2>
    </a>
    <p class="post-meta">Posted on {{ post.date.strftime('%B %d, %Y') }}</p>
</div>
{% endfor %}
```

## Known Issues & Quirks
- `config.json` contains plaintext credentials and should be gitignored
- Port 80 requires elevated privileges (sudo on Unix, admin on Windows)
- Template folder spelled `template/` not `templates/` (non-standard Flask convention)
- Static CSS exists in two locations: `static/styles.css` and `static/css/styles.css` (templates reference the latter)
- Model string lengths are restrictive: `Posts.content` is only 120 chars (should be Text type for blog posts)
- No admin interface for creating/editing posts - requires direct database access
