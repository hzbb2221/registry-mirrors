FROM registry.cn-guangzhou.aliyuncs.com/hzbb/python:3.7.0

MAINTAINER hzbb2221

EXPOSE 15000

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime &&\
	echo 'Asia/Shanghai' >/etc/timezone 


COPY ./ /registry-mirrors
WORKDIR /registry-mirrors

RUN pip install -r ./website-monitor/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

CMD python3 ./website-monitor/website_monitor.py 