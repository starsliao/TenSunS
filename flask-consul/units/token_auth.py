from flask_httpauth import HTTPTokenAuth
import sys
sys.path.append("..")
from config import s

auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(token):
    try:
        data = s.loads(token)
    except:
        return False
    return True
