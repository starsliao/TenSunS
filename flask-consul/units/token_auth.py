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
    #except BadSignature:
        #raise AuthFailed(msg='token不正确')
    except SignatureExpired:
        raise AuthFailed(msg='token过期')
        return {"code": 40000, "data": "登录过期，请重新登录！"}
    except:
        return False
    return True
