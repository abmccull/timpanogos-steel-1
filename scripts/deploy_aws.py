import os
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)

class AWSDeployer:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.cloudfront = boto3.client('cloudfront')
        self.acm = boto3.client('acm', region_name='us-east-1')  # ACM must be in us-east-1 for CloudFront
        
        # Load configuration
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'timpanogos-steel-website')
        self.domain_name = os.getenv('SITE_DOMAIN', 'timpanogos-steel.com')
        self.region = os.getenv('AWS_REGION', 'us-east-1')

    def create_s3_bucket(self):
        """Create and configure S3 bucket for static website hosting"""
        try:
            logging.info(f"Creating S3 bucket: {self.bucket_name}")
            
            # Create bucket
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )

            # Enable static website hosting
            self.s3.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': '404.html'}
                }
            )

            # Configure bucket policy for public read access
            bucket_policy = {
                'Version': '2012-10-17',
                'Statement': [{
                    'Sid': 'PublicReadGetObject',
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': 's3:GetObject',
                    'Resource': f'arn:aws:s3:::{self.bucket_name}/*'
                }]
            }
            self.s3.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=str(bucket_policy)
            )

            logging.info("S3 bucket created and configured successfully")
            return True

        except ClientError as e:
            logging.error(f"Error creating S3 bucket: {str(e)}")
            return False

    def upload_files(self, build_dir):
        """Upload files to S3 bucket"""
        try:
            logging.info(f"Uploading files from {build_dir} to S3")
            
            # Walk through the build directory
            for root, _, files in os.walk(build_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    # Calculate S3 key (path within bucket)
                    s3_key = os.path.relpath(local_path, build_dir)
                    
                    # Set content type based on file extension
                    content_type = self._get_content_type(file)
                    
                    # Upload file
                    with open(local_path, 'rb') as f:
                        self.s3.upload_fileobj(
                            f,
                            self.bucket_name,
                            s3_key,
                            ExtraArgs={
                                'ContentType': content_type,
                                'CacheControl': 'max-age=86400'  # 24 hour cache
                            }
                        )
                    logging.info(f"Uploaded {s3_key}")

            logging.info("All files uploaded successfully")
            return True

        except ClientError as e:
            logging.error(f"Error uploading files: {str(e)}")
            return False

    def request_certificate(self):
        """Request SSL certificate from ACM"""
        try:
            logging.info(f"Requesting SSL certificate for {self.domain_name}")
            
            # Request certificate
            response = self.acm.request_certificate(
                DomainName=self.domain_name,
                ValidationMethod='DNS',
                SubjectAlternativeNames=[f'www.{self.domain_name}']
            )
            
            certificate_arn = response['CertificateArn']
            logging.info(f"Certificate requested. ARN: {certificate_arn}")
            
            return certificate_arn

        except ClientError as e:
            logging.error(f"Error requesting certificate: {str(e)}")
            return None

    def create_cloudfront_distribution(self, certificate_arn):
        """Create CloudFront distribution"""
        try:
            logging.info("Creating CloudFront distribution")
            
            # Distribution configuration
            distribution_config = {
                'CallerReference': datetime.now().isoformat(),
                'Aliases': {
                    'Quantity': 2,
                    'Items': [self.domain_name, f'www.{self.domain_name}']
                },
                'DefaultRootObject': 'index.html',
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': 'S3Origin',
                        'DomainName': f'{self.bucket_name}.s3.amazonaws.com',
                        'S3OriginConfig': {'OriginAccessIdentity': ''}
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'S3Origin',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'AllowedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD'],
                        'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 86400,
                    'MaxTTL': 31536000
                },
                'ViewerCertificate': {
                    'ACMCertificateArn': certificate_arn,
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.2_2021'
                },
                'Enabled': True,
                'Comment': 'Timpanogos Steel Website Distribution'
            }
            
            # Create distribution
            response = self.cloudfront.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_id = response['Distribution']['Id']
            domain_name = response['Distribution']['DomainName']
            
            logging.info(f"CloudFront distribution created. ID: {distribution_id}")
            logging.info(f"Distribution domain name: {domain_name}")
            
            return distribution_id, domain_name

        except ClientError as e:
            logging.error(f"Error creating CloudFront distribution: {str(e)}")
            return None, None

    def _get_content_type(self, filename):
        """Determine content type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon'
        }
        return content_types.get(ext, 'application/octet-stream')

def main():
    """Main deployment function"""
    try:
        # Initialize deployer
        deployer = AWSDeployer()
        
        # Create and configure S3 bucket
        if not deployer.create_s3_bucket():
            raise Exception("Failed to create S3 bucket")
        
        # Upload files
        build_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build')
        if not deployer.upload_files(build_dir):
            raise Exception("Failed to upload files")
        
        # Request SSL certificate
        certificate_arn = deployer.request_certificate()
        if not certificate_arn:
            raise Exception("Failed to request SSL certificate")
        
        # Create CloudFront distribution
        distribution_id, domain_name = deployer.create_cloudfront_distribution(certificate_arn)
        if not distribution_id:
            raise Exception("Failed to create CloudFront distribution")
        
        logging.info("Deployment completed successfully!")
        logging.info(f"Website will be available at: https://{deployer.domain_name}")
        logging.info("Note: DNS configuration and certificate validation required to complete setup")
        
    except Exception as e:
        logging.error(f"Deployment failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()
