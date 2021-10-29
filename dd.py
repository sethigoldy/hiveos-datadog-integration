from datadog import initialize, api
import time
import os

options = {
    'api_key': os.getenv("dd_key"),
    ## EU costumers need to define 'api_host' as below
    'api_host': 'https://api.datadoghq.eu/'
}

initialize(**options)

now = time.time()
future_10s = now + 10

def send_metrics(key,value):
    # Submit a single point with a timestamp of `now`
    try:
        value=float(value)
    except Exception as ex:
        return
    if type(value) != str:
        print("sending %s key and %s value" % (key, value))
        api.Metric.send(metric=key, points=value, type="gauge")

# # Submit a point with a timestamp (must be current)
# api.Metric.send(metric='my.pair', points=(now, 15))

# # Submit multiple points.
# api.Metric.send(
#     metric='my.series',
#     points=[
#         (now, 15),
#         (future_10s, 16)
#     ]
# )

# Submit a point with a host and tags.
# api.Metric.send(
#     metric='my.series',
#     points=100,
#     host="myhost.example.com",
#     tags=["version:1"]
# )

# # Submit multiple metrics
# api.Metric.send([{
#     'metric': 'my.series',
#     'points': 15
# }, {
#     'metric': 'my1.series',
#     'points': 16
# }])
