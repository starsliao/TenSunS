import os
from itsdangerous import TimedJSONWebSignatureSerializer

consul_token = os.environ.get('consul_token','a94d1ecb-81d3-ea0a-4dc8-5e6701e528c5')
consul_url = os.environ.get('consul_url','http://10.5.148.67:8500/v1')
admin_passwd = os.environ.get('admin_passwd','cass.007')
secret_key = os.environ.get('secret_key',consul_token)
s = TimedJSONWebSignatureSerializer(secret_key)
