# HiveOS Datadog Integration

HiveOS integration with Datadog(DD), this will capture data from all of your HiveOS farms and send it to Datadog as metric by using which one can build beautiful dashboards, create monitors on DD, trigger incidents accordingly always stay top on any incident with your mining operation.

## Working

The application will start by fetching your mining pool stats (`mine_pool_url` if provided in environment var), then authenticates your HiveOS account by reading OTP from your gmail account and passing it to `auth/login` API. After authentication it reads current stats of your HiveOS farm data (can work on multiple farms in one account) and sends all the data to DD as `gauge` type.

P.S. - Added Heroku Procfile for one click setup.

## To start locally first set env variables run following commands

```
hive_email=<gmail_address>
hive_password=<gmail_password>
email=<hive_login_email>
password=<hive_login_password>
dd_key=<datadog_api_key>
mine_pool_url=<wallet_json_get_api_url> # optional but can be helpful if one wants to calculate their earnings on DD
pip install -r requirements.txt
python hiveos.py
```

Currently in alpha version (WIP), if you found any issues please raise them in Github I would try my best to resolve them. Cheers!!!!  

`MIT License 2021`
