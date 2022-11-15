"""
截取前端ldap信息存入consul
"""
from units import consul_kv


class Ldap_Consul():

    """
    存储ldap信息
    """
    @staticmethod
    def set_consul_args(**kwargs):
        kwargs['port'] = int(kwargs.get("port"))
        result = consul_kv.put_kv(f'ConsulManager/ldap/report', {**kwargs})
        if result:
            return True
        return False


    """
    获取ldap信息进行链接服务端
    """
    @staticmethod
    def get_consul_args(**kwargs):
        result = consul_kv.get_kv_dict("ConsulManager/ldap/report")
        try:
            result.get("ConsulManager/ldap/report").get("ldap_url")
        except Exception:
            return False
        return result.get("ConsulManager/ldap/report").get("ldap_url"),\
               result.get("ConsulManager/ldap/report").get("port"),\
               result.get("ConsulManager/ldap/report").get("rule"),\
               result.get("ConsulManager/ldap/report").get("password")
