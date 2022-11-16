"""
ldap 用户认证
"""

from ldap3 import Server, Connection, ALL

from units.ldap.ldap_consul import Ldap_Consul


class Ldap(object):
    def __init__(self,**args):
        ldap_dict = Ldap_Consul.get_consul_args(**args)
        if ldap_dict:
            self.ldap_url,self.port,self.rule,self.password,self.ldapusr,self.allow = ldap_dict
            server = Server(self.ldap_url,port=self.port, get_info=ALL,connect_timeout=5)
            self.conn = Connection(server, user=self.rule, password=self.password, auto_bind=True)
        else:
            self.allow = ''
    #校验登录
    def authpass(self, username, password):
        if self.allow == '':
            return 0
        if self.allow == '*' or username.lower() in self.allow.lower().split(','):
            ldap_username = self.ldapusr.format(username=username)
            print('ldapuser:',ldap_username,flush=True)
            server = Server(self.ldap_url,port=self.port, get_info=ALL,connect_timeout=5)
            conn = Connection(server, user=ldap_username, password=password, check_names=True, lazy=False, raise_exceptions=False)
            try:
                conn.bind()
            except Exception:
                conn.bind()

            if conn.result["description"] == "success":
                data = 1
            else:
                data = 3
        else:
            data = 2
        return data


    #连接
    def conn_ldap(self):
        self.conn.search('dc=lishicloud,dc=com', '(objectclass=person)',
                    attributes=['cn', 'displayName', 'departmentNumber'])
        entry = self.conn.response
        return entry


    #获取用户
    def get_user(self,username=None,all=False):
        ldap_user = []
        if all == False:
            try:
                result = self.conn_ldap()
            except Exception:
                result = self.conn_ldap()

            for user in result:
                users = user.get("raw_attributes").get("cn")[0].decode("utf8")
                if users == username:
                    try:
                        users = user.get("raw_attributes").get("displayName")[0].decode("utf-8")
                        return users
                    except Exception as e:
                        return False
        else:
            result = self.conn_ldap()
            for user in result:
                users = user.get("raw_attributes").get("cn")[0].decode("utf8")
                ldap_user.append(users)
            return ldap_user

    #创建用户
    def create_user(self):
        objectclass = ['top', 'inetOrgPerson', 'posixAccount']
        c = self.conn.add('uid=user1,ou=People,dc=xxx,dc=com',objectclass,
                               {'cn': "user1", 'sn': 'user1',"employeeType":"developer",
                                'gidNumber': 501, 'homeDirectory': '/home/users/{0}', 'uidNumber': 5000,"givenName":"user1",
                                "loginShell":"/bin/bash",'displayName': "测试用户",'userPassword': "111111", 'mail': 'user1@qq.com'}),
        print(c)


    #删除用户
    def delete_user(self):
        c = self.conn.delete('cn=xxx,ou=People,dc=xxx,dc=com')
        print(c)

    # def __del__(self):
    #     self.conn.delete()


if __name__ == '__main__':
    ldap = Ldap()
    result = ldap.delete_user()
    print(result)
