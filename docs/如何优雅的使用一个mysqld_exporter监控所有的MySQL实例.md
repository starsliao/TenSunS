# 如何优雅的使用一个mysqld_exporter监控所有的MySQL实例
### 如何在ConsulManager中接入云厂商的数据库
1. 新增云账号的情况：目前新增时，支持多选区域，以及选择增加的资源类型，勾选MySQL即可接入自动同步云数据库，记得设置好同步间隔。
![图片](https://user-images.githubusercontent.com/3349611/199262165-3582e051-a924-4043-bc05-96643b17caca.png)

2. 对已经添加过的账号，增加同步云数据库资源：点击编辑云资源，选择好需要编辑的厂商、账号及区域，再勾选资源类型MySQL，配置上同步间隔即可增加自动同步云数据库。
![图片](https://user-images.githubusercontent.com/3349611/199263994-c9485241-d8bb-46b2-abd8-48084de94236.png)
