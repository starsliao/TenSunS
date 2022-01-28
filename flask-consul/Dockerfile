FROM python:3-alpine
ADD . /
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
#&& sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
EXPOSE 2026
CMD ["python3","/flaskconsul.py"]
