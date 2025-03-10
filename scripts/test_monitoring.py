import logging
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_test.log'),
        logging.StreamHandler()
    ]
)

class MockCloudWatch:
    def __init__(self):
        self.metric_data = []
        self.alarms = {
            'page-load-time': {'StateValue': 'OK'},
            'form-submission-rate': {'StateValue': 'OK'},
            'high-bounce-rate': {'StateValue': 'OK'},
            'page-generation-errors': {'StateValue': 'OK'},
            'form-completion-time': {'StateValue': 'OK'},
            'high-form-abandonment': {'StateValue': 'OK'},
            'low-city-page-views-business-hours': {'StateValue': 'OK'}
        }

    def put_metric_data(self, **kwargs):
        self.metric_data.append(kwargs)
        self._evaluate_alarms(kwargs)
        return {'ResponseMetadata': {'HTTPStatusCode': 200}}

    def describe_alarms(self):
        return {'MetricAlarms': [
            {'AlarmName': name, **state} 
            for name, state in self.alarms.items()
        ]}

    def _evaluate_alarms(self, metric_data):
        namespace = metric_data['Namespace']
        for datapoint in metric_data['MetricData']:
            metric_name = datapoint['MetricName']
            value = datapoint['Value']

            # Simulate alarm evaluation based on thresholds
            if metric_name == 'PageLoadTime' and value > 2000:
                self._update_alarm('page-load-time', 'ALARM', 'Page load time exceeded threshold')
            elif metric_name == 'FormSubmissions' and value < 3:
                self._update_alarm('form-submission-rate', 'ALARM', 'Low form submission rate')
            elif metric_name == 'BounceRate' and value > 70:
                self._update_alarm('high-bounce-rate', 'ALARM', 'High bounce rate detected')
            elif metric_name == 'GenerationErrors' and value > 0:
                self._update_alarm('page-generation-errors', 'ALARM', 'Page generation error detected')
            elif metric_name == 'FormCompletionTime' and value > 300:
                self._update_alarm('form-completion-time', 'ALARM', 'Form completion time exceeded threshold')
            elif metric_name == 'FormAbandonment' and value > 60:
                self._update_alarm('high-form-abandonment', 'ALARM', 'High form abandonment rate')
            elif metric_name == 'CityPageViews' and value < 15:
                self._update_alarm('low-city-page-views-business-hours', 'ALARM', 'Low city page views')

    def _update_alarm(self, alarm_name, state, reason):
        self.alarms[alarm_name] = {
            'StateValue': state,
            'StateReason': reason,
            'StateUpdatedTimestamp': datetime.utcnow()
        }

class MonitoringTester:
    def __init__(self):
        self.cloudwatch = MockCloudWatch()
        self.namespace = 'TimpanogosSteel'

    def put_test_metric(self, metric_name, value, unit='Count', namespace=None):
        """Put a test metric data point"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace=namespace or self.namespace,
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit,
                    'Timestamp': datetime.utcnow().isoformat()
                }]
            )
            logging.info(f"Put test metric: {metric_name} = {value} {unit}")
            return True
        except Exception as e:
            logging.error(f"Error putting metric {metric_name}: {str(e)}")
            return False

    def test_performance_alerts(self):
        """Test performance-related alerts"""
        logging.info("\nTesting performance alerts...")

        # Test page load time (should trigger alert)
        self.put_test_metric(
            'PageLoadTime',
            3000,  # 3 seconds, above 2s threshold
            'Milliseconds',
            f'{self.namespace}/Performance'
        )

        # Test multiple slow page loads
        for i in range(3):
            self.put_test_metric(
                'PageLoadTime',
                2500,  # 2.5 seconds
                'Milliseconds',
                f'{self.namespace}/Performance'
            )

    def test_form_alerts(self):
        """Test form-related alerts"""
        logging.info("\nTesting form alerts...")

        # Test form completion time (should trigger alert)
        self.put_test_metric(
            'FormCompletionTime',
            400,  # 400 seconds, above 5-minute threshold
            'Seconds',
            f'{self.namespace}/Forms'
        )

        # Test form abandonment (should trigger alert)
        for i in range(10):
            self.put_test_metric(
                'FormAbandonment',
                75,  # 75% abandonment rate
                'Percent',
                f'{self.namespace}/Forms'
            )

        # Test low form submissions (should trigger alert)
        self.put_test_metric(
            'FormSubmissions',
            1,  # Below 3/day threshold
            'Count',
            f'{self.namespace}/Forms'
        )

    def test_engagement_alerts(self):
        """Test engagement-related alerts"""
        logging.info("\nTesting engagement alerts...")

        # Test high bounce rate (should trigger alert)
        for i in range(6):
            self.put_test_metric(
                'BounceRate',
                80,  # 80% bounce rate
                'Percent',
                f'{self.namespace}/Engagement'
            )

        # Test low city page views (should trigger alert)
        for hour in range(8):  # Test 8 business hours
            self.put_test_metric(
                'CityPageViews',
                10,  # Below 15/hour threshold
                'Count',
                f'{self.namespace}/Traffic'
            )

    def test_error_alerts(self):
        """Test error-related alerts"""
        logging.info("\nTesting error alerts...")

        # Test page generation errors (should trigger immediate alert)
        self.put_test_metric(
            'GenerationErrors',
            1,  # Any error should trigger
            'Count',
            f'{self.namespace}/PageGeneration'
        )

    def verify_alarms(self):
        """Verify alarm states"""
        try:
            alarms = self.cloudwatch.describe_alarms()
            logging.info("\nCurrent Alarm States:")
            for alarm in alarms['MetricAlarms']:
                state = alarm['StateValue']
                name = alarm['AlarmName']
                reason = alarm.get('StateReason', 'No reason provided')
                
                if state == 'ALARM':
                    logging.info(f"⚠️  {name}")
                    logging.info(f"   State: {state}")
                    logging.info(f"   Reason: {reason}\n")
                else:
                    logging.info(f"✓ {name}: {state}\n")

        except Exception as e:
            logging.error(f"Error verifying alarms: {str(e)}")

def main():
    tester = MonitoringTester()
    
    # Run tests
    tester.test_performance_alerts()
    tester.test_form_alerts()
    tester.test_engagement_alerts()
    tester.test_error_alerts()
    
    # Verify alarm states
    tester.verify_alarms()

if __name__ == '__main__':
    main()
