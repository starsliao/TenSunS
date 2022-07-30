# 🏷目录
- [云主机自动同步JumpServer能做什么？](#云主机自动同步jumpserver能做什么)
- [同步JumpServer功能如何开启？](#同步jumpserver功能如何开启)
- [如何获取JumpServer永久token？](#如何获取jumpserver永久token)
- [什么是JumpServer的管理用户？](#什么是jumpserver的管理用户)
- [接入JumpServer时，`全局通用主机【管理用户】信息`该如何填写？](#接入jumpserver时全局通用主机管理用户信息该如何填写)
- [接入JumpServer时，`全局特殊主机【管理用户】信息`该如何填写？](#接入jumpserver时全局特殊主机管理用户信息该如何填写)
- [接入JumpServer操作完成之后，我该做什么？](#接入jumpserver操作完成之后我该做什么)
- [高级设置：不同云账号有不同的jumpserver管理账户的场景能否支持？](#高级设置不同云账号有不同的jumpserver管理账户的场景能否支持)


## 云主机自动同步JumpServer能做什么？
- 当您在云上购买了新的ECS时，需要手动在JumpServer中创建新资产来纳管该ECS。
- `JumpServer同步`功能可以把阿里、腾讯、华为云的ECS资源自动同步到JumpServer中，免去手动创建资产的操作。
- 当您在云厂商界面新增、删除、修改ECS后，都会及时的自动同步到JumpServer中。

## 同步JumpServer功能如何开启？
![图片](https://user-images.githubusercontent.com/3349611/180848168-a2bafcfa-faa1-457d-8f5f-dcb07ad12d60.png)

## 如何获取JumpServer永久token？
- 登录JumpServer所在的主机，执行以下命令：
```
docker exec -it jms_core /bin/bash   #非容器化部署的JumpServer，不执行该行。
cd /opt/jumpserver/apps
python manage.py shell
from users.models import User
u = User.objects.get(username='admin')   #admin换成你的JumpServer管理员用户名。
```
- 该账号没有创建过token的执行以下命令：`u.create_private_token()`
- 该账号已经创建过token的执行以下命令：`u.private_token`
- 记录`PrivateToken: `后面的部分，最后的`>`不要。

## 什么是JumpServer的管理用户？
- 管理用户是资产（被控服务器）上的 root，或拥有 NOPASSWD: ALL sudo 权限的用户， JumpServer 使用该用户来 `推送系统用户`、`获取资产硬件信息` 等。
- 创建资产的时候需要给每台ECS选择一个管理用户：
![图片](https://user-images.githubusercontent.com/3349611/180855383-ec4a76b3-9354-4485-b0f6-17b5b9c2a8d7.png)

## 接入JumpServer时，`全局通用主机【管理用户】信息`该如何填写？
![图片](https://user-images.githubusercontent.com/3349611/180858510-b2b4ac0f-bc01-4c8e-a948-f3f26338037e.png)

- 全局通用是指：全局是指所有的云账号，一般情况下所有的ECS会使用一个统一的管理用户来方便管理ECS。
- Linux需要创建一个有root权限的管理用户。
- Windows可以不需要管理用户，创建一个，账号密码随意填写即可。
- 端口即为ssh（linux）或者远程桌面（windows）的端口。
- 管理用户ID即为管理用户的ID，点击相应的管理用户即可看到ID。
![图片](https://user-images.githubusercontent.com/3349611/180858937-856a7f9a-afa9-46d5-a15d-514f13063af5.png)

- 配置完成之后所有的Linux主机都会使用对应的Linux端口和Linux管理用户。

## 接入JumpServer时，`全局特殊主机【管理用户】信息`该如何填写？
![图片](https://user-images.githubusercontent.com/3349611/180859728-6c1e7c41-ea75-4efa-98ca-6b26266d71e7.png)
- 对于部分主机可能会使用特殊的端口以及管理用户的情况，所以我们支持了根据主机名称关键字来匹配不同的登录端口和管理用户的功能。
- 实例如下：
```
{
    "xxxaaa": {
        "linux": [
            ["ssh/22"],
            "b510418c-ea15-44d8-836a-5eb6138a6c56"
        ]
    },
    "xxxbbb": {
        "linux": [
            ["ssh/2626"],
            "b510418c-ea15-44d8-836a-5eb6138a6c56"
        ],
        "windows": [
            ["rdp/3389"],
            "21a7d079-319b-483f-b31c-bf92254f1ac7"
        ]
    }
}
```
说明：
- 填写的内容必须是一个Json格式。
- 最外层的key：`xxxaaa`、`xxxbbb`表示主机名的关键字，包含该关键字的主机均有效。
- 每个最外层key的value为固定格式：有windows或者linux系统的端口和管理用户ID，您只需要更换掉对应的端口号及管理用户ID即可。

## 接入JumpServer操作完成之后，我该做什么？
- 完成接入后，您将看到已经接入过数据源的云厂商账号的信息，包括整体的系统、资源、状态信息，如图：
![图片](https://user-images.githubusercontent.com/3349611/180862967-4575fbdf-3bb4-47ae-a491-df00eaba9a26.png)
- 点击各云账号右侧的同步开关，填写节点信息和同步间隔后，即可进行首次同步（耗时依主机数而定，可在日志中查看进度）。
- `新节点ID`：节点即为JumpServer中，存放资产的目录。对于每个云账号**必须新建一个节点**来存放该账号的ECS，防止同步操作对已有节点的主机造成影响。
- 在JumpServer-资产管理-资产列表-资产树中，右键点击根节点（Default），即可`创建节点`，对创建的节点点右键选择最后的`显示节点详情`即可查看节点ID。
![图片](https://user-images.githubusercontent.com/3349611/180865099-f95c1a9c-851c-489d-9e88-403661ef469b.png)
- 同步完成后，即可在界面上看到资源数和同步的ECS数量，**注意：JumpServer中已有的同名主机不会同步**，如数量不一致，可在日志从查看同名主机信息。
- 最后，可以登录JumpServer，找到对应到节点，查看同步后的主机信息，会根据云资源的分组信息把所有的ECS存放到对应的分组目录。

**注意：云主机自动同步JumpServer功能仅是自动化了创建资产的操作，每台云主机的系统用户，还需要根据JumpServer的配置来创建或者推送。**

---

## 高级设置：不同云账号有不同的jumpserver管理账户的场景能否支持？
### 目前web界面上不支持这样的场景，不过后端是已经支持的，所以可以直接修改consul KV的方式来实现。
- 访问consul的webUI `http://x.x.x.x:8500/ui/dc1/kv/ConsulManager/jms/`
- 该目录下可以看到2个键：全局管理用户信息：`ecs_info`，全局特殊管理用户信息：`custom_ecs_info`
- 进入改目录下对应的云厂商以及云账户的目录
- 把上面提到了两个键复制到云账户的目录下即可，并修改为需要的内容即可，注意内容的格式保持不变。
- 下次同步时候会优先读取云账户目录下的管理用户信息。（需要登录jumpserver删掉已同步的主机。）
- 我会尽快把这个功能做到web界面上。
