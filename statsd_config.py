import statsd
from flask import request
from logging_config import logger

statsd_client = statsd.StatsClient('127.0.0.1', 8125)


def handle_metric_count(status):
    metric_name = "API: " + request.path + "API Method: " + request.method + status
    logger.info(f"metric incremented {metric_name}")
    print(metric_name)
    statsd_client.incr(metric_name, 1) 
