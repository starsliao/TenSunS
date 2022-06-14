from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer
from units import consul_kv
secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk']
s = TimedJSONWebSignatureSerializer(secret_key,expires_in=28800)
auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(token):
    try:
        data = s.loads(token)
    except:
        return False
    return True
