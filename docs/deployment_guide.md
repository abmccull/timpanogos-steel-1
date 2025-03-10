# Timpanogos Steel Website Deployment Guide

## Prerequisites

1. AWS Account with appropriate permissions:
   - S3 full access
   - CloudFront full access
   - ACM (Certificate Manager) access
   - IAM access for creating service roles

2. AWS CLI installed and configured
3. Python 3.11.4+ with required packages
4. Domain name registered and accessible

## Initial Setup

1. **Create Environment File**
   ```bash
   cp .env.example .env
   ```
   Update the following AWS-specific variables:
   ```ini
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-east-1
   AWS_S3_BUCKET=timpanogos-steel-website
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Deployment Steps

1. **Generate Static Pages**
   ```bash
   python scripts/generate_pages.py
   ```
   This will create HTML files in the `build/` directory.

2. **Run AWS Deployment**
   ```bash
   python scripts/deploy_aws.py
   ```
   This script will:
   - Create S3 bucket if not exists
   - Configure bucket for static website hosting
   - Request SSL certificate
   - Create CloudFront distribution
   - Upload all files from `build/` directory

3. **DNS Configuration**
   After deployment, you'll need to:
   1. Get the CloudFront distribution domain name from the deployment logs
   2. Create/update DNS records:
      - Create an A record pointing to the CloudFront distribution
      - Create a CNAME record for 'www' subdomain

4. **SSL Certificate Validation**
   1. Check AWS Certificate Manager console
   2. Add the CNAME records provided by ACM to your DNS
   3. Wait for validation (can take up to 30 minutes)

## Post-Deployment Verification

1. **Check Website Accessibility**
   - Visit https://timpanogos-steel.com
   - Verify HTTPS is working
   - Check www subdomain redirect

2. **Form Testing**
   - Submit test forms from different sections
   - Verify submissions in Google Sheets
   - Check email notifications

3. **Analytics Verification**
   - Confirm Google Analytics tracking
   - Verify Sentry error tracking
   - Check CloudFront logs

## Monitoring

1. **AWS CloudWatch**
   - Monitor S3 metrics
   - Check CloudFront distribution metrics
   - Set up alarms for errors

2. **Google Analytics**
   - Monitor page views
   - Track form submissions
   - Analyze user behavior

3. **Sentry**
   - Monitor JavaScript errors
   - Track form submission errors
   - Set up error alerts

## Troubleshooting

1. **SSL Certificate Issues**
   - Verify DNS records are correct
   - Check certificate status in ACM console
   - Ensure CloudFront is using the correct certificate

2. **Form Submission Errors**
   - Check Google Apps Script logs
   - Verify reCAPTCHA configuration
   - Confirm Google Sheets permissions

3. **CloudFront Issues**
   - Check distribution status
   - Verify origin settings
   - Clear cache if needed

## Security Notes

1. **Access Management**
   - Regularly rotate AWS access keys
   - Use IAM roles with minimal required permissions
   - Enable MFA for AWS users

2. **SSL/TLS**
   - Maintain valid SSL certificates
   - Use TLS 1.2 or higher
   - Monitor certificate expiration

3. **Form Security**
   - Monitor for spam submissions
   - Keep reCAPTCHA keys secure
   - Regular security audits

## Maintenance

1. **Regular Updates**
   - Update Python dependencies
   - Check for AWS SDK updates
   - Monitor Google Apps Script versions

2. **Backup Strategy**
   - Regular S3 bucket backups
   - Export Google Sheets data
   - Backup configuration files

3. **Performance Optimization**
   - Monitor CloudFront cache hit ratio
   - Optimize image sizes
   - Review page load times

## Support

For deployment issues or questions, contact:
- Development Team
- AWS Support (if applicable)
- Domain Registrar Support
