import statsd
from flask import request
statsd_client = statsd.StatsClient('127.0.0.1', 8125)

def handle_metric_count(status):
    print(request.method)
    print(request.path)
    metric_name = "API: " + request.path + "API Method: " + request.method + status
    statsd_client.incr(metric_name, 1) 
