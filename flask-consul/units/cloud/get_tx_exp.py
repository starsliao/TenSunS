#!/usr/bin/python3
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.billing.v20180709 import billing_client, models
try:
    cred = credential.Credential("AKIDWqwnOjpgHchX7SYP1NUMyKQGrCI8j40g", "TgdLn0xe5HDtJUQ6WgMqCKEuNdfS1LRJ")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "billing.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = billing_client.BillingClient(cred, "", clientProfile)

    req = models.DescribeAccountBalanceRequest()
    params = {

    }
    req.from_json_string(json.dumps(params))

    resp = client.DescribeAccountBalance(req).RealBalance
    print(resp/100)

except TencentCloudSDKException as err:
    print(err)
