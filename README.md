# Timpanogos Steel Website Generator

A scalable, SEO-optimized platform for generating over 11,000 city-state landing pages for Timpanogos Steel's building solutions.

## Project Structure

```
/
├── docs/              # Generated HTML pages for GitHub Pages
├── data/             # CSV files with city-specific content
├── templates/        # HTML templates
│   ├── base.html    # Main template with dynamic content
│   └── form.html    # Reusable form component
├── scripts/         # Python automation scripts
│   ├── generate_pages.py  # Page generation script
│   └── form_handler.gs    # Google Apps Script for form handling
├── static/          # Static assets
│   ├── css/        # Stylesheets
│   ├── js/         # JavaScript files
│   └── images/     # Image assets
└── requirements.txt # Python dependencies
```

## Hosting Architecture

### GitHub Pages
- Static site hosting directly from repository
- Serves from `/docs` directory
- Automatic builds on push
- Version control and collaboration

### Cloudflare Integration
- Global CDN with 250+ edge locations
- Free SSL/TLS certificates
- DDoS protection
- Caching and optimization
- Analytics and monitoring

## Setup Instructions

### 1. Environment Setup

1. Install Python 3.11.4 or later
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### 2. GitHub Pages Setup

1. Push repository to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. Enable GitHub Pages:
   - Go to repository Settings
   - Navigate to Pages section
   - Select main branch and /docs folder
   - Save configuration

### 3. Cloudflare Setup

1. Create Cloudflare account
2. Add your domain
3. Update nameservers with registrar
4. Configure Page Rules:
   - Enable caching
   - Set SSL/TLS to Full
   - Configure edge rules

### 2. Form Handling Setup

1. Create a new Google Sheet for lead capture
2. Open Google Apps Script editor and create a new project
3. Copy the contents of `scripts/form_handler.gs` into the editor
4. Update the following variables in the script:
   - `SPREADSHEET_ID`: Your Google Sheet ID
   - `SHEET_NAME`: Name for the submissions sheet (default: "Form Submissions")
   - Replace `your-email@example.com` with your notification email

5. Deploy the script as a web app:
   - Click "Deploy" > "New deployment"
   - Choose "Web app" as the type
   - Set "Execute as" to "Me"
   - Set "Who has access" to "Anyone"
   - Click "Deploy"
   - Copy the deployment URL

6. Set up reCAPTCHA:
   - Visit [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin)
   - Register your site
   - Get your Site Key and Secret Key

7. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Update with your actual values:
   - `FORM_ENDPOINT`: Google Apps Script deployment URL
   - `RECAPTCHA_SITE_KEY`: reCAPTCHA site key
   - `RECAPTCHA_SECRET_KEY`: reCAPTCHA secret key
   - `SPREADSHEET_ID`: Google Sheet ID
   - Other configuration values

### 3. Page Generation

1. Prepare your city data CSV file with required columns:
   - City, State, Latitude, Longitude
   - Introduction (300 words)
   - CityIntro (100 words)
   - ResidentialContent, CommercialContent, IndustrialContent, AgriculturalContent

2. Run the page generator:
   ```bash
   python scripts/generate_pages.py
   ```

3. Generated pages will be in the `docs/` directory with SEO-friendly URLs:
   - Format: `steel-buildings-[city]-[state].html`
   - Example: `steel-buildings-salt-lake-city-utah.html`

## Features

- **SEO Optimization**
  - Dynamic meta tags
  - Schema.org LocalBusiness markup
  - SEO-friendly URLs
  - City-specific content

- **Lead Generation**
  - Multiple CTA forms
  - reCAPTCHA integration
  - Google Sheets integration
  - Email notifications

- **Analytics & Monitoring**
  - Google Analytics integration
  - Sentry error tracking
  - Form submission tracking
  - Comprehensive logging

## Development Process

1. Environment setup with Python 3.11.4
2. Template creation with Jinja2
3. CSV processing with Pandas
4. Batch generation (100 pages at a time)
5. Form handling setup
6. AWS deployment (upcoming)

## Security Notes

- Never commit `.env` file with sensitive keys
- Always use reCAPTCHA for form submissions
- Keep Google Apps Script access tokens secure
- Monitor form submissions for spam

## Maintenance

- Regularly update the CSV data
- Monitor Google Sheets capacity
- Check form submission logs
- Update dependencies as needed

## Support

For issues or questions, please contact the development team.
