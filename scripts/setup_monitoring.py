import os
import boto3
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_setup.log'),
        logging.StreamHandler()
    ]
)

class MonitoringSetup:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Validate required environment variables
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_REGION',
            'AWS_CLOUDFRONT_DISTRIBUTION_ID',
            'AWS_S3_BUCKET',
            'MONITORING_EMAIL'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Initialize AWS clients
        self.cloudwatch = boto3.client(
            'cloudwatch',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # Store configuration
        self.distribution_id = os.getenv('AWS_CLOUDFRONT_DISTRIBUTION_ID')
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.alarm_email = os.getenv('MONITORING_EMAIL')
        self.region = os.getenv('AWS_REGION')
        
        logging.info(f"Initialized monitoring setup for region {self.region}")

    def setup_s3_monitoring(self):
        """Set up S3 bucket monitoring"""
        try:
            logging.info("Setting up S3 monitoring")
            
            # Monitor bucket size
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.bucket_name}-size-alarm",
                MetricName='BucketSizeBytes',
                Namespace='AWS/S3',
                Statistic='Average',
                Period=86400,  # 24 hours
                EvaluationPeriods=1,
                Threshold=10000000000,  # 10GB
                ComparisonOperator='GreaterThanThreshold',
                AlarmActions=[self.alarm_email],
                Dimensions=[
                    {'Name': 'BucketName', 'Value': self.bucket_name}
                ]
            )

            # Monitor number of objects
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.bucket_name}-objects-alarm",
                MetricName='NumberOfObjects',
                Namespace='AWS/S3',
                Statistic='Average',
                Period=86400,
                EvaluationPeriods=1,
                Threshold=15000,  # Alert if more than 15,000 objects
                ComparisonOperator='GreaterThanThreshold',
                AlarmActions=[self.alarm_email],
                Dimensions=[
                    {'Name': 'BucketName', 'Value': self.bucket_name}
                ]
            )

            logging.info("S3 monitoring configured successfully")
            return True

        except Exception as e:
            logging.error(f"Error setting up S3 monitoring: {str(e)}")
            return False

    def setup_cloudfront_monitoring(self):
        """Set up CloudFront distribution monitoring"""
        try:
            logging.info("Setting up CloudFront monitoring")
            
            # Monitor error rate
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.distribution_id}-error-rate",
                MetricName='5xxErrorRate',
                Namespace='AWS/CloudFront',
                Statistic='Average',
                Period=300,  # 5 minutes
                EvaluationPeriods=2,
                Threshold=2,  # 2% error rate
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',  # Don't alert on missing data
                AlarmActions=[self.alarm_email],
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.distribution_id}
                ]
            )

            # Monitor 4xx error rate
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.distribution_id}-4xx-error-rate",
                MetricName='4xxErrorRate',
                Namespace='AWS/CloudFront',
                Statistic='Average',
                Period=300,  # 5 minutes
                EvaluationPeriods=3,
                Threshold=5,  # 5% error rate
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                AlarmActions=[self.alarm_email],
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.distribution_id}
                ]
            )

            # Monitor cache hit rate
            self.cloudwatch.put_metric_alarm(
                AlarmName=f"{self.distribution_id}-cache-hit-rate",
                MetricName='CacheHitRate',
                Namespace='AWS/CloudFront',
                Statistic='Average',
                Period=3600,  # 1 hour
                EvaluationPeriods=3,
                Threshold=80,  # Below 80% cache hit rate
                ComparisonOperator='LessThanThreshold',
                TreatMissingData='ignore',  # Ignore missing data for cache metrics
                AlarmActions=[self.alarm_email],
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.distribution_id}
                ]
            )

            logging.info("CloudFront monitoring configured successfully")
            return True

        except Exception as e:
            logging.error(f"Error setting up CloudFront monitoring: {str(e)}")
            return False

    def setup_custom_metrics(self):
        """Set up custom metrics for application monitoring"""
        try:
            logging.info("Setting up custom metrics")
            
            # Monitor form submissions with composite alarm
            self.cloudwatch.put_metric_alarm(
                AlarmName='form-submission-rate',
                MetricName='FormSubmissions',
                Namespace='TimpanogosSteel/Forms',
                Statistic='Sum',
                Period=86400,  # 24 hours
                EvaluationPeriods=1,
                Threshold=3,  # Alert if less than 3 submissions per day
                ComparisonOperator='LessThanThreshold',
                TreatMissingData='breaching',  # Alert if no data (potential tracking issues)
                AlarmActions=[self.alarm_email]
            )

            # Monitor page load time with percentile
            self.cloudwatch.put_metric_alarm(
                AlarmName='page-load-time',
                MetricName='PageLoadTime',
                Namespace='TimpanogosSteel/Performance',
                ExtendedStatistic='p90',  # Use 90th percentile
                Period=300,  # 5 minutes
                EvaluationPeriods=3,
                Threshold=2000,  # 2 seconds
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                AlarmActions=[self.alarm_email]
            )

            # Monitor form completion time with dynamic threshold
            self.cloudwatch.put_metric_alarm(
                AlarmName='form-completion-time',
                MetricName='FormCompletionTime',
                Namespace='TimpanogosSteel/Forms',
                Statistic='Average',
                Period=3600,  # 1 hour
                EvaluationPeriods=2,
                Threshold=300,  # 5 minutes
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='ignore',
                DatapointsToAlarm=2,  # Must have 2 breaching datapoints
                AlarmActions=[self.alarm_email]
            )

            # Monitor bounce rate with anomaly detection
            self.cloudwatch.put_metric_alarm(
                AlarmName='high-bounce-rate',
                MetricName='BounceRate',
                Namespace='TimpanogosSteel/Engagement',
                Statistic='Average',
                Period=3600,  # 1 hour
                EvaluationPeriods=6,
                Threshold=70,  # 70% bounce rate
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                DatapointsToAlarm=4,  # Must have 4 out of 6 breaching points
                AlarmActions=[self.alarm_email]
            )

            # Monitor city page views with time-based threshold
            self.cloudwatch.put_metric_alarm(
                AlarmName='low-city-page-views-business-hours',
                MetricName='CityPageViews',
                Namespace='TimpanogosSteel/Traffic',
                Statistic='Sum',
                Period=3600,  # 1 hour
                EvaluationPeriods=8,  # Business hours
                Threshold=15,  # Minimum 15 views per hour during business hours
                ComparisonOperator='LessThanThreshold',
                TreatMissingData='breaching',
                AlarmActions=[self.alarm_email]
            )

            # Monitor form abandonment rate with sliding window
            self.cloudwatch.put_metric_alarm(
                AlarmName='high-form-abandonment',
                MetricName='FormAbandonment',
                Namespace='TimpanogosSteel/Forms',
                Statistic='Average',
                Period=1800,  # 30 minutes
                EvaluationPeriods=48,  # 24-hour sliding window
                Threshold=60,  # 60% abandonment rate
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                DatapointsToAlarm=36,  # 75% of periods must breach
                AlarmActions=[self.alarm_email]
            )

            # Monitor page generation errors with immediate alert
            self.cloudwatch.put_metric_alarm(
                AlarmName='page-generation-errors',
                MetricName='GenerationErrors',
                Namespace='TimpanogosSteel/PageGeneration',
                Statistic='Sum',
                Period=60,  # 1 minute
                EvaluationPeriods=1,
                Threshold=0,
                ComparisonOperator='GreaterThanThreshold',
                TreatMissingData='notBreaching',
                AlarmActions=[self.alarm_email]
            )

            logging.info("Custom metrics configured successfully")
            return True

        except Exception as e:
            logging.error(f"Error setting up custom metrics: {str(e)}")
            return False

    def create_dashboard(self):
        """Create CloudWatch dashboard"""
        try:
            logging.info("Creating CloudWatch dashboard")
            
            dashboard = {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/CloudFront", "Requests", "DistributionId", self.distribution_id],
                                [".", "5xxErrorRate", ".", "."],
                                [".", "4xxErrorRate", ".", "."]
                            ],
                            "period": 300,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "CloudFront Metrics"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/S3", "BucketSizeBytes", "BucketName", self.bucket_name],
                                [".", "NumberOfObjects", ".", "."]
                            ],
                            "period": 86400,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "S3 Metrics"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["TimpanogosSteel/Forms", "FormSubmissions"],
                                ["TimpanogosSteel/Forms", "FormCompletionTime"],
                                ["TimpanogosSteel/Forms", "FormAbandonment"]
                            ],
                            "period": 3600,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "Form Metrics"
                        }
                    },
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["TimpanogosSteel/Performance", "PageLoadTime"],
                                ["TimpanogosSteel/Traffic", "CityPageViews"],
                                ["TimpanogosSteel/Engagement", "BounceRate"]
                            ],
                            "period": 3600,
                            "stat": "Average",
                            "region": "us-east-1",
                            "title": "Performance & Engagement"
                        }
                    }
                ]
            }

            self.cloudwatch.put_dashboard(
                DashboardName='TimpanogosSteel',
                DashboardBody=str(dashboard)
            )

            logging.info("Dashboard created successfully")
            return True

        except Exception as e:
            logging.error(f"Error creating dashboard: {str(e)}")
            return False

def main():
    """Main execution function"""
    try:
        monitoring = MonitoringSetup()
        
        # Set up all monitoring components
        s3_success = monitoring.setup_s3_monitoring()
        cloudfront_success = monitoring.setup_cloudfront_monitoring()
        metrics_success = monitoring.setup_custom_metrics()
        dashboard_success = monitoring.create_dashboard()
        
        if all([s3_success, cloudfront_success, metrics_success, dashboard_success]):
            logging.info("All monitoring components set up successfully")
        else:
            logging.warning("Some monitoring components failed to set up")
            
    except Exception as e:
        logging.error(f"Error in monitoring setup: {str(e)}")
        raise

if __name__ == '__main__':
    main()
