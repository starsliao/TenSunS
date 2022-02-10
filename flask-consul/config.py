import os
from itsdangerous import TimedJSONWebSignatureSerializer

consul_token = os.environ.get('consul_token','635abc53-c18c-f780-58a9-f04feb28fef1')
consul_url = os.environ.get('consul_url','http://10.0.0.26:8500/v1')
admin_passwd = os.environ.get('admin_passwd','123456')
secret_key = os.environ.get('secret_key',consul_token)
s = TimedJSONWebSignatureSerializer(secret_key)
