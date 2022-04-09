from pyDes import des, ECB, PAD_PKCS5
import binascii, consul_kv
secret_key = consul_kv.get_value('ConsulManager/assets/secret/skey')['sk']
key = secret_key[:8]
iv = key
k = des(key, ECB, iv, pad=None, padmode=PAD_PKCS5)

def encrypt(s):
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en).decode()

def decrypt(s):
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de.decode()
