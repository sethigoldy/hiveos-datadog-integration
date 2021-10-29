import json
import os
import dd
import time
import gmail
import requests
from requests import api
import sched, time
from flask import Flask, request


app = Flask(__name__)

s = sched.scheduler(time.time, time.sleep)

api_endpoint = "https://api2.hiveos.farm/api/v2/"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_otp_hive():
    get_otp_ep = "auth/login/confirmation"
    response = requests.post(api_endpoint+get_otp_ep,
        headers=headers,
        data=json.dumps({
            "login":os.getenv('hive_email')
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
    return 0


def auth_hive():
    otp = get_otp_hive()
    auth_api_url = "auth/login"
    if otp > 0:
        # we have otp, send login request
        response = requests.post(api_endpoint + auth_api_url,
            headers=headers,
            data=json.dumps({
                "login": os.getenv("hive_email"),
                "password": os.getenv("hive_password"),
                "twofa_code": str(otp),
                "remember": True
            })
        )
        print("auth login status code",response.status_code)
        if response.status_code == 200:
            data = response.json()
            if data.get("access_token", None):
                return data.get("access_token")
    print("Unable to get bearer token from hive api")
    return ""


def get_farm_data():
    bearer_token = auth_hive()
    auth_header = {
        "Authorization": "Bearer %s" % bearer_token,
        'Host': os.getenv("host")
    }
    print(auth_header)
    response = requests.get(api_endpoint+"farms", headers={**auth_header, **headers})
    if response.status_code == 200:
        farms_data = response.json()
        # from pprint import pprint; pprint(farms_data)
        for farm in farms_data:
            data = farm.get("data",{})
            send_metrics_chain(data)


def send_metrics_chain(data, key="hive"):
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


def start_metrics():
    print("Monitoring start...")
    s.enter(300, 1, send_metrics_chain, (s,))
    s.run()


if __name__ == "__main__":
    start_metrics()
