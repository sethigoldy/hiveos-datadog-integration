# HiveOS Datadog Integration

HiveOS integration with Datadog(DD), this will capture data from all of your HiveOS farms and send it to Datadog as metric by using which one can build beautiful dashboards, create monitors on DD, trigger incidents accordingly always stay top on any incident with your mining operation.

Added Heroku Procfile for one click setup.

## To start locally first set env variables run following commands

```
hive_email=<gmail_address>
hive_password=<gmail_password>
email=<hive_login_email>
password=<hive_login_password>
host=<host_website_address>  # need this due to cloudflare SSL
pip install -r requirements.txt
python hiveos.py
```

Currently in alpha version (WIP)

MIT License 2021
