# 如何优雅的使用一个mysqld_exporter监控所有的MySQL实例
### 如何在ConsulManager中接入云厂商的数据库
1. 新增云账号的情况：目前新增时，支持多选区域，以及选择增加的资源类型，勾选MySQL即可接入自动同步云数据库，记得设置好同步间隔。

![图片](https://user-images.githubusercontent.com/3349611/199262165-3582e051-a924-4043-bc05-96643b17caca.png)

2. 对已经添加过的账号，增加同步云数据库资源：点击编辑云资源，选择好需要编辑的厂商、账号及区域，再勾选资源类型MySQL，配置上同步间隔即可增加自动同步云数据库。

![图片](https://user-images.githubusercontent.com/3349611/199264858-f2a325bf-fad2-4850-bc39-76e9271d883e.png)

3. 接入完成后，可手动点击同步按钮，完成首次同步；或者等待设定好的同步周期后会自动同步。

![图片](https://user-images.githubusercontent.com/3349611/199267039-a010ce6f-3e04-4e54-8e44-6bde7ff5a000.png)

### 
