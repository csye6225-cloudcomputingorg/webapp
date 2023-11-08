import statsd
from flask import request
from logging_config import logger

statsd_client = statsd.StatsClient(host='localhost', port=8125)


def handle_metric_count(status):
    metric_name = f'{request.path}_{request.method}_{status}'
    logger.info(f"metric incremented {metric_name}")
    statsd_client.incr(metric_name)
