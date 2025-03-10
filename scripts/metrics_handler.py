import os
import json
import boto3
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metrics_api.log'),
        logging.StreamHandler()
    ]
)

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.cloudwatch = boto3.client('cloudwatch')
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests for metrics"""
        try:
            # Only handle /api/metrics endpoint
            if urlparse(self.path).path != '/api/metrics':
                self.send_error(404, "Endpoint not found")
                return

            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            metric_data = json.loads(post_data.decode('utf-8'))

            # Validate required fields
            required_fields = ['MetricName', 'Value', 'Unit']
            if not all(field in metric_data for field in required_fields):
                self.send_error(400, "Missing required fields")
                return

            # Send metric to CloudWatch
            self.send_metric_to_cloudwatch(metric_data)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success'}).encode())

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logging.error(f"Error processing metric: {str(e)}")
            self.send_error(500, "Internal server error")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_metric_to_cloudwatch(self, metric_data):
        """Send metric to CloudWatch"""
        try:
            namespace = metric_data.get('Namespace', 'TimpanogosSteel')
            timestamp = metric_data.get('Timestamp', datetime.utcnow().isoformat())

            self.cloudwatch.put_metric_data(
                Namespace=namespace,
                MetricData=[{
                    'MetricName': metric_data['MetricName'],
                    'Value': float(metric_data['Value']),
                    'Unit': metric_data['Unit'],
                    'Timestamp': timestamp
                }]
            )

            logging.info(f"Sent metric to CloudWatch: {metric_data['MetricName']}")

        except Exception as e:
            logging.error(f"Error sending metric to CloudWatch: {str(e)}")
            raise

def run_metrics_server(port=8081):
    """Run the metrics server"""
    try:
        server_address = ('', port)
        httpd = HTTPServer(server_address, MetricsHandler)
        logging.info(f"Starting metrics server on port {port}")
        httpd.serve_forever()
    except Exception as e:
        logging.error(f"Error starting metrics server: {str(e)}")
        raise

if __name__ == '__main__':
    run_metrics_server()
