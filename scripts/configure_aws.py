import os
import boto3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_aws_config():
    """Set up AWS configuration"""
    try:
        # Create .aws directory if it doesn't exist
        aws_dir = Path.home() / '.aws'
        aws_dir.mkdir(exist_ok=True)
        
        # Create config file
        config_file = aws_dir / 'config'
        with open(config_file, 'w') as f:
            f.write(f"""[default]
region = us-east-1
output = json
""")
        
        # Create credentials file
        credentials_file = aws_dir / 'credentials'
        with open(credentials_file, 'w') as f:
            f.write(f"""[default]
aws_access_key_id = {os.getenv('AWS_ACCESS_KEY_ID')}
aws_secret_access_key = {os.getenv('AWS_SECRET_ACCESS_KEY')}
""")
        
        logging.info("AWS configuration files created successfully")
        
        # Test AWS configuration
        try:
            session = boto3.Session()
            client = session.client('sts')
            response = client.get_caller_identity()
            logging.info(f"AWS configuration verified. Account ID: {response['Account']}")
            return True
        except Exception as e:
            logging.error(f"AWS configuration verification failed: {str(e)}")
            return False
            
    except Exception as e:
        logging.error(f"Error setting up AWS configuration: {str(e)}")
        return False

if __name__ == '__main__':
    setup_aws_config()
