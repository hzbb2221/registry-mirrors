#!/bin/bash

# 使用阿里云源安装必须组件
pip install -r ./website-monitor/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 启动程序
python3 ./website-monitor/website_monitor.py 