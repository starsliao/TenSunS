#!/bin/bash
uuid=`uuidgen`
echo ""
read -p "请设置登录后羿运维平台的admin密码：" passwd
if [ -z $passwd ]; then
  passwd="tensuns"
  echo -e "\n未输入，使用默认密码：\033[31;1mtensuns\033[0m\n"
fi

cat <<EOF > 1.consul-deploy.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tensuns
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: consul-config
  namespace: tensuns
  labels:
    app: consul
data:
  consul.hcl: |+
    log_level = "error"
    data_dir = "/consul/data"
    client_addr = "0.0.0.0"
    ui_config {
      enabled = true
    }
    ports = {
      grpc = -1
      https = -1
      dns = -1
      grpc_tls = -1
      serf_wan = -1
    }
    peering {
      enabled = false
    }
    connect {
      enabled = false
    }
    acl = {
      enabled = true
      default_policy = "deny"
      enable_token_persistence = true
      tokens {
        initial_management = "$uuid"
        agent = "$uuid"
      }
    }
    server = true
    bootstrap_expect = 1
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: consul
  namespace: tensuns
  labels:
    app: consul
spec:
  replicas: 1
  selector:
    matchLabels:
      app: consul
  template:
    metadata:
      labels:
        app: consul
    spec:
      volumes:
        - name: consul-config
          configMap:
            name: consul-config
      containers:
        - name: consul
          image: hashicorp/consul:1.16
          ports:
            - name: http
              containerPort: 8500
              protocol: TCP
          env:
            - name: TZ
              value: Asia/Shanghai
          volumeMounts:
            - name: consul-data
              mountPath: /consul/data
            - name: consul-config
              mountPath: /consul/config/consul.hcl
              subPath: consul.hcl
          imagePullPolicy: IfNotPresent
      restartPolicy: Always
  volumeClaimTemplates:
    - kind: PersistentVolumeClaim
      apiVersion: v1
      metadata:
        name: consul-data
        namespace: tensuns
        annotations:
          everest.io/disk-volume-type: SAS
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 10Gi
        storageClassName: csi-disk
        volumeMode: Filesystem
  serviceName: consul

---
apiVersion: v1
kind: Service
metadata:
  name: consul
  namespace: tensuns
  labels:
    app: consul
spec:
  ports:
    - name: http
      protocol: TCP
      port: 8500
      targetPort: 8500
  selector:
    app: consul
  type: ClusterIP
EOF

cat <<EOF > 2.tensuns-deploy.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tensuns
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: flask-consul
  namespace: tensuns
  labels:
    app: flask-consul
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-consul
  template:
    metadata:
      labels:
        app: flask-consul
    spec:
      initContainers:
        - name: wait-for-consul
          image: busybox
          command:
            - sh
            - '-c'
            - >-
              for i in \$(seq 1 60); do nc -z -w3 consul 8500 && exit 0 ||
              sleep 5; done; exit 1
          imagePullPolicy: IfNotPresent
      containers:
        - name: flask-consul
          image: 'swr.cn-south-1.myhuaweicloud.com/starsl.cn/flask-consul:latest'
          ports:
            - name: http-2026
              containerPort: 2026
              protocol: TCP
          env:
            - name: admin_passwd
              value: '$passwd'
            - name: consul_token
              value: '$uuid'
            - name: consul_url
              value: 'http://consul:8500/v1'
            - name: log_level
              value: INFO
            - name: TZ
              value: Asia/Shanghai
          imagePullPolicy: Always
      restartPolicy: Always
---
kind: Service
apiVersion: v1
metadata:
  name: flask-consul
  namespace: tensuns
  labels:
    app: flask-consul
spec:
  ports:
    - name: http-2026
      protocol: TCP
      port: 2026
      targetPort: 2026
  selector:
    app: flask-consul
  type: ClusterIP
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: nginx-consul
  namespace: tensuns
  labels:
    app: nginx-consul
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-consul
  template:
    metadata:
      labels:
        app: nginx-consul
    spec:
      containers:
        - name: nginx-consul
          image: 'swr.cn-south-1.myhuaweicloud.com/starsl.cn/nginx-consul:latest'
          ports:
            - name: http-1026
              containerPort: 1026
              protocol: TCP
          env:
            - name: TZ
              value: Asia/Shanghai
          imagePullPolicy: Always
      restartPolicy: Always
---
kind: Service
apiVersion: v1
metadata:
  name: tensuns
  namespace: tensuns
  labels:
    app: tensuns
spec:
  ports:
    - name: nginx-consul
      protocol: TCP
      port: 1026
      targetPort: 1026
      nodePort: 31026
  selector:
    app: nginx-consul
  type: NodePort
  externalTrafficPolicy: Cluster
EOF
