import os
import dd
import time
import json
import gmail
import requests
from requests import api
import sched, time
from flask import Flask, request
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

MINE_POOL=os.getenv("mine_pool_url")
HIVE_EMAIL=os.getenv('hive_email')
HIVE_PASSWORD=os.getenv("hive_password")
HOST_ENV=os.getenv("host")
TTL=os.getenv("ttl")

s = sched.scheduler(time.time, time.sleep)

api_endpoint = "https://api2.hiveos.farm/api/v2/"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


@app.route("/")
def index():
    return "Hello World!"


def get_otp_hive(retry = 0):
    current_otp = 0
    try:
        get_otp_ep = "auth/login/confirmation"
        response = requests.post(api_endpoint+get_otp_ep,
            headers=headers,
            data=json.dumps({
                "login":HIVE_EMAIL
            })
        )
        if response.status_code == 200:
            time.sleep(5)
            otps = gmail.get_otp()
            if len(otps) >= 1:
                current_otp = otps[0]
                print(current_otp)
                return current_otp
        print("Unable to get otp from email")
        if current_otp == 0 and retry <= 1:
            return get_otp_hive(retry=retry+1)
    except Exception as ex:
        if retry <= 1:
            return get_otp_hive(retry = retry+1)
    return current_otp


def auth_hive():
    if cache.get("hive_auth_token"):
        return cache.get("hive_auth_token")
    otp = get_otp_hive()
    auth_api_url = "auth/login"
    if otp > 0:
        # we have otp, send login request
        response = requests.post(api_endpoint + auth_api_url,
            headers=headers,
            data=json.dumps({
                "login": HIVE_EMAIL,
                "password": HIVE_PASSWORD,
                "twofa_code": str(otp),
                "remember": True
            })
        )
        print("auth login status code",response.status_code)
        if response.status_code == 200:
            data = response.json()
            if data.get("access_token", None):
                cache.set("hive_auth_token",data.get("access_token"), timeout=data.get("expires_in"))
                return data.get("access_token")
    print("Unable to get bearer token from hive api")
    return ""


def send_metrics_chain(data, key=""):
    if data is None:
        return
    if type(data) is list:
        for k,metric in enumerate(data):
            n_key = "%s.%s" % (key,str(k)) if key else str(k)
            send_metrics_chain(metric, n_key)
    elif type(data) is dict:
        for k,metric in data.items():
            n_key = "%s.%s" % (key,str(k)) if key else str(k)
            send_metrics_chain(metric, n_key)
    else:
        dd.send_metrics(key,data)


def get_farm_data():
    bearer_token = auth_hive()
    auth_header = {
        "Authorization": "Bearer %s" % bearer_token,
        'Host': HOST_ENV
    }
    response = requests.get(api_endpoint+"farms", headers={**auth_header, **headers})
    if response.status_code == 200:
        farms_data = response.json()
        # from pprint import pprint; pprint(farms_data)
        farms_data = farms_data.get("data")
        for farm in farms_data :
            send_metrics_chain(farm, key="hive")
        print("Round completed with DD")


def send_mining_wallet():
    if MINE_POOL:
        extra_headers = {
            "host": HOST_ENV,
        }
        response = requests.get(MINE_POOL,headers={**headers, **extra_headers})
        if response.status_code == 200:
            data = response.json()
            if data.get("rewards",None):
                del data["rewards"]
            if data.get("sumrewards",None):
                del data["sumrewards"]
            print("Sending mining metrics to DD")
            send_metrics_chain(data, key="pool")


def start_metrics():
    if not (HIVE_EMAIL and HIVE_PASSWORD and os.getenv('email') 
            and os.getenv('password') and os.getenv("dd_key") and TTL):
        print("Please set all environment variables before starting.")
        exit(1)
    try: 
        print("Monitoring start...")
        send_mining_wallet()
        get_farm_data()
    except Exception as ex:
        print(ex)
        print("Unable to fetch data!!!")
    s.enter(int(TTL), 1, start_metrics, (s,))
    s.run()


start_metrics()

