from flask import Flask, render_template
import subprocess
from datetime import datetime, timedelta
import sqlite3
import time
import threading

app = Flask(__name__)

# 要监控的网站列表
TARGETS = [
    "cr.laoyou.ip-ddns.com",
    "func.ink",
    "proxy.1panel.live",
    "hub.littlediary.cn",
    "docker-0.unsee.tech",
    "docker.zhai.cm",
    "a.ussh.net",
    "docker.1ms.run",
    "docker.melikeme.cn",
    "image.cloudlayer.icu",
    "docker.1panelproxy.com",
    "lispy.org",
    "docker.hlmirror.com",
    "docker.1panel.live",
    "docker.wanpeng.top",
    "docker.xiaogenban1993.com",
    "docker-mirror.aigc2d.com",
    "docker.1panel.top",
    "docker.kejilion.pro",
    "dockerpull.cn",
    "docker.xuanyuan.me",
    "docker.anye.in",
    "dhub.kubesre.xyz",
    "hub.fast360.xyz"
]

# 初始化数据库
def init_db():
    conn = sqlite3.connect('status.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS status
                 (target TEXT, timestamp TEXT, status INTEGER,
                  PRIMARY KEY (target, timestamp))''')
    conn.commit()
    conn.close()

# 检查网站状态
def check_status(target):
    try:
        result = subprocess.run(
            ['docker', 'pull', target + '/library/busybox:1.35.0'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        return result.returncode == 0
    except:
        return False

# 后台监控
def monitor():
    init_db()
    while True:
        for target in TARGETS:
            status = 1 if check_status(target) else 0
            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect('status.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO status VALUES (?, ?, ?)", 
                     (target, timestamp, status))
            conn.commit()
            conn.close()
        
        time.sleep(300)  # 每5分钟检查一次

@app.route('/')
def index():
    conn = sqlite3.connect('status.db')
    c = conn.cursor()
    
    stats = {}
    for target in TARGETS:
        # 获取1天数据
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-1 day')", (target,))
        total1 = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-1 day') AND status = 1", (target,))
        success1 = c.fetchone()[0]
        day1 = round((success1 / total1) * 100, 2) if total1 > 0 else 0
        
        # 获取7天数据
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-7 days')", (target,))
        total7 = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-7 days') AND status = 1", (target,))
        success7 = c.fetchone()[0]
        day7 = round((success7 / total7) * 100, 2) if total7 > 0 else 0
        
        # 获取30天数据
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-30 days')", (target,))
        total30 = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM status WHERE target = ? AND timestamp > datetime('now', '-30 days') AND status = 1", (target,))
        success30 = c.fetchone()[0]
        day30 = round((success30 / total30) * 100, 2) if total30 > 0 else 0
        
        stats[target] = {
            'day1': day1,
            'day7': day7,
            'day30': day30
        }
    
    conn.close()
    
    # 按24小时可用性排序
    # sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1]['day1'], reverse=True))
    # 多级排序：按1天、7天、30天可用性降序
    sorted_stats = dict(sorted(
        stats.items(),
        key=lambda x: (x[1]['day1'], x[1]['day7'], x[1]['day30']),
        reverse=True
    ))

    return render_template('index.html', stats=sorted_stats)

if __name__ == '__main__':
    # 启动后台监控
    threading.Thread(target=monitor, daemon=True).start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=15000)

