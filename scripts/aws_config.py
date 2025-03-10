import os
import boto3
import logging
from dotenv import load_dotenv

def configure_aws():
    """Configure AWS credentials and settings from environment variables"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Required AWS configuration
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Configure boto3 session
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Test connection
        cloudwatch = session.client('cloudwatch')
        cloudwatch.list_metrics(Namespace='AWS/CloudWatch')
        
        logging.info(f"AWS configuration successful. Region: {aws_region}")
        return True
        
    except Exception as e:
        logging.error(f"Error configuring AWS: {str(e)}")
        return False

if __name__ == '__main__':
    configure_aws()
