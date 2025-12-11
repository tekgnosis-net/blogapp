# blogapp

A Flask-based blog application with MySQL database backend, designed for deployment on Google Cloud Platform.

## Features

- Blog post management with slug-based URLs
- Contact form for visitor submissions
- MySQL database with SQLAlchemy ORM
- Start Bootstrap "Clean Blog" responsive theme
- GCP Cloud SQL integration ready

## Quick Start

### Prerequisites

- Python 3.x
- MySQL database (local or GCP Cloud SQL)
- Root/admin privileges for port 80 (or modify to use port 5000)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tekgnosis-net/blogapp.git
cd blogapp
```

2. Install dependencies:
```bash
pip install -r blogapp/requirements.txt
```

3. Configure database:
   - Edit `blogapp/config.json` with your database credentials
   - Update `local_server` flag in `blogapp/__init__.py` (line 10)
   - For local MySQL: Set connection string on line 15
   - For GCP Cloud SQL: Update socket path with your project details

4. Initialize database (first run only):
```bash
cd blogapp
python __init__.py
```
   **Important**: After first run, comment out `create_table()` on line 79 of `__init__.py`

5. Run the application:
```bash
cd blogapp
python __init__.py
```

The app will be available at `http://localhost:80`

### Using Docker

#### Quick Start with Docker Compose
```bash
# Start the application with MySQL database
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop the application
docker-compose down
```

The app will be available at `http://localhost:5000`

#### Build and Run Docker Image Manually
```bash
# Build the image
docker build -t blogapp:latest .

# Run the container (requires external MySQL)
docker run -d \
  -p 5000:5000 \
  -e PORT=5000 \
  -e DEBUG=False \
  --name blogapp \
  blogapp:latest
```

#### Pull from GitHub Container Registry
```bash
# Pull the latest image
docker pull ghcr.io/tekgnosis-net/blogapp:latest

# Run the pulled image
docker run -d -p 5000:5000 ghcr.io/tekgnosis-net/blogapp:latest
```

## Project Structure

```
blogapp/
├── __init__.py          # Main Flask application (routes, models, config)
├── config.json          # Database credentials and GCP settings
├── requirements.txt     # Python dependencies
├── template/           # Jinja2 templates
│   ├── layout.html     # Base template
│   ├── index.html      # Homepage
│   ├── about.html      # About page
│   ├── contact.html    # Contact form
│   └── post.html       # Individual post view
└── static/             # Static assets (CSS, JS, images)
    └── css/
        └── styles.css  # Start Bootstrap theme
```

## Database Models

### Posts
- `sno`: Primary key
- `title`: Post title (80 chars)
- `slug`: URL-friendly identifier (25 chars)
- `content`: Post content (120 chars - consider extending to Text type)
- `date`: Publication timestamp

### Contacts
- `sno`: Primary key
- `name`: Visitor name (80 chars)
- `email`: Email address (50 chars)
- `phone_num`: Phone number (12 chars)
- `mes`: Message content (120 chars)
- `date`: Submission timestamp

## Routes

- `/` - Homepage (currently shows static template posts)
- `/about` - About page
- `/contact` - Contact form (GET/POST)
- `/post/<slug>` - Individual blog post by slug

## Known Limitations

- **No admin interface**: Posts must be created via direct database access
- **No authentication**: No login system or user management
- **Static homepage**: `index.html` shows hardcoded sample posts instead of database content
- **No contact notifications**: Contact submissions stored but no email alerts
- **Restrictive field lengths**: Post content limited to 120 chars (needs migration to Text type)

## GCP Deployment

The app is configured for Google Cloud Platform deployment:

1. Update `config.json` with your GCP project details:
   - `PROJECT_ID`: Your GCP project ID
   - `INSTANCE_NAME`: Cloud SQL instance name
   - `PUBLIC_IP_ADDRESS`: Cloud SQL external IP

2. Update Cloud SQL socket path in `__init__.py` line 15:
   ```python
   unix_socket=/cloudsql/{PROJECT_ID}:{REGION}:{INSTANCE_NAME}
   ```

3. Use GCP Secret Manager for production credentials instead of `config.json`

## Docker Images

Docker images are automatically built and pushed to GitHub Container Registry (GHCR) on every push to the repository.

**Available tags:**
- `latest` - Latest build from master branch
- `master` - Latest build from master branch
- `<branch-name>` - Latest build from specific branch
- `v*` - Semantic version tags (e.g., v1.0.0)
- `<branch>-<sha>` - Specific commit SHA

**GitHub Actions Workflow:**
The `.github/workflows/docker-build.yml` workflow automatically:
- Builds Docker images on every push
- Pushes images to `ghcr.io/tekgnosis-net/blogapp`
- Tags images appropriately based on branch/tag
- Uses Docker layer caching for faster builds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

[Add your license here]

## To-Do

- [ ] Implement admin interface with Flask-Login
- [ ] Add authentication and user management
- [ ] Convert homepage to dynamic database-driven posts
- [ ] Migrate Post.content to Text field type
- [ ] Add form validation and CAPTCHA to contact form
- [ ] Implement email notifications for contact submissions
- [ ] Add .gitignore for config.json and sensitive files
- [ ] Create database migration scripts