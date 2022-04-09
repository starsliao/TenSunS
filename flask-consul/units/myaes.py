# encoding:utf-8
from base64 import b64encode,b64decode
from Crypto.Util.Padding import pad,unpad
from Crypto.Cipher import AES
import consul_kv
secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk'].encode('utf8')

def encrypt(data):
    data = data.encode('utf8')
    cipher = AES.new(secret_key, AES.MODE_CBC)
    encrypted_data = cipher.encrypt(pad(data, 16))
    data = cipher.iv + encrypted_data
    return b64encode(data).decode('utf8')
 
def decrypt(data):
    data = b64decode(data)
    iv = data[:16]
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    data = unpad(cipher.decrypt(data[16:]), 16)
    return data.decode('utf8')
