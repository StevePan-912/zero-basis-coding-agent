import time
from typing import Dict
from datetime import datetime

class Monitoring:
    """监控系统"""

    def __init__(self):
        self.api_metrics: Dict = {}
        self.error_count = 0
        self.request_count = 0

    def record_api_call(self, endpoint: str, response_time: float, success: bool):
        """记录API调用"""
        self.request_count += 1
        if not success:
            self.error_count += 1

        if endpoint not in self.api_metrics:
            self.api_metrics[endpoint] = {
                'total_calls': 0,
                'avg_response_time': 0,
                'success_count': 0,
                'error_count': 0
            }

        metrics = self.api_metrics[endpoint]
        metrics['total_calls'] += 1

        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1

        metrics['avg_response_time'] = (
            (metrics['avg_response_time'] * (metrics['total_calls'] - 1) + response_time)
            / metrics['total_calls']
        )

    def get_metrics(self) -> Dict:
        """获取监控指标"""
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'api_metrics': self.api_metrics,
            'timestamp': datetime.now().isoformat()
        }

monitoring = Monitoring()