#! /usr/bin/python
# encoding:utf-8

import time
import requests
import os
import delegator
import requests
requests.packages.urllib3.disable_warnings()
from utils import ping
import socket

def get_python():
    c = delegator.run('pipenv run which python')
    return c.out.strip()


def get_headers(useragent):
    if not useragent.strip():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Range': 'bytes=0-1040000'
        }
    headers = {}
    for item in useragent.split("\n"):
        item = item.strip()
        if len(item.split(":")) != 2:
            continue
        k, v = item.split(":")
        headers[k.strip()] = v.strip()
    return headers

def format_reason(reason):
    if isinstance(reason, bytes):
        try:
            reason = reason.decode('utf-8')
        except UnicodeDecodeError:
            reason = reason.decode('iso-8859-1')
    return reason

def browser_check(url):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    chrome_script = os.path.join(cur_dir, 'utils/chrome.py')
    cmd = "{python} {script} {url}".format(
        python=get_python(),
        script=chrome_script,
        url=url
    )
    c = delegator.run(cmd)

    ret = c.out.strip().split('chrome:')[1]
    status_code, reason = ret.split('-')
    return int(status_code), reason

def http_check(url, useragent='', method='get', retry=1, timeout=10, data=None, is_301=False):
    start_time = time.time()
    headers = get_headers(useragent)
    try:
        # requests的timeout参数含义是( connect , read ) 连接最大是10s,配置里是读取时间
        # 所以,理论最大可能花费70s

        # 调整超时设置,暂时写死30,30
        if method == 'head':
            r = requests.head(url, timeout=(10, timeout), headers=headers, verify=False)
        elif method == 'post':
            r = requests.post(url, data=data, timeout=(10, timeout), headers=headers, verify=False)
        else:
            r = requests.get(url, timeout=(20, 30), headers=headers, verify=False)

        tim = '%.2f' % ((time.time() - start_time) * 1000)

        status_code = r.status_code
        reason = format_reason(r.reason)

        # 如果不允许重定向,但是出现了重定向,返回错误.
        if r.history and not is_301:
            status_code = r.history[0].status_code
            reason = format_reason(r.history[0].reason)
            res = '0'
            return {'res': res, 'sta': ' '.join([str(status_code), reason]), 'tim': tim}

        # 反爬虫特殊处理
        if status_code == 521:
            # 因为里面执行了两次url，如果跳转的话结果就可能出现302
            # 所以这里需要拿到最后一跳的url
            status_code, reason = browser_check(url)
        tim = '%.2f' % ((time.time() - start_time) * 1000)

        # 正常
        if status_code < 300:
            res = '1'
        else:  # 400 <= status_code < 600 client && server error
            res = '0'

        return {'res': res, 'status_code': status_code,'reason':reason, 'tim': tim}

    except Exception as e:  # URLError是HTTPError祖先,
        reason = str(e)
        if 'Connection refused' in reason:
            sta = 'Connection refused'
        elif 'Connection aborted' in reason:
            sta = 'Connection aborted'
        elif 'Read timed out' in reason:
            sta = 'Read timed out'
        elif 'timed out' in reason:
            sta = 'timed out'
        elif 'Name or service not known' in reason:
            sta = 'Name or service not known'
        elif 'Network is unreachable' in reason:
            sta = 'Network is unreachable'
        elif 'Failed to establish a new connection' in reason:
            sta = 'Failed to establish a new connection'
        else:
            sta = reason[:40]
        tim = '%.2f' % ((time.time() - start_time) * 1000)
        return {'res': '0', 'sta': sta, 'tim': tim}


def ping_check(host, lossrate=0, threshold=1):

    start_time = time.time()
    res = '0'
    percent_lost, mrtt, _ = ping.quiet_ping(host, timeout=10, count=4)  # 返回值表示丢失率(0~100),最大耗时(ms),平均耗时(ms)

    try:
        percent_lost, mrtt, _ = ping.quiet_ping(host, timeout=10, count=4)  # 返回值表示丢失率(0~100),最大耗时(ms),平均耗时(ms)
        tim = '%.2f' % ((time.time() - start_time) * 1000)
        if percent_lost == 100:
            return {"res": '0', "tim": tim, "sta": 'PING LOSS', "loss": percent_lost}

        if percent_lost == lossrate:
            if mrtt < threshold * 1000:
                res = '1'
                sta = 'PING OK'
            else:
                res = '0'
                sta = 'PING LONG'
        else:
            res = '0'
            sta = 'PING LOSS'

    except:
        sta = 'Unknown Error'
        tim = '%.2f' % ((time.time() - start_time) * 1000)
        percent_lost = 100

    ret = {"res": res, "tim": tim, "sta": sta, "loss": percent_lost}
    return ret


def tcp_check(ip, port, timeout=5):
    try:
        res = '1'
        start_time = time.time()
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cs.settimeout(timeout)
        address = (str(ip), int(port))
        status = cs.connect_ex((address))
        tim = '%.2f' % ((time.time() - start_time) * 1000)
        # this status is returnback from tcpserver
        if status == 0:
            res = '1'
            sta = 'TCP_CONNECT_OK'
        else:
            res = '0'
            sta = 'TCP_CONNECT_ERR'

    except:
        res = '0'
        tim = '%.2f' % ((time.time() - start_time) * 1000)
        sta = 'TCP_CONNECT_ERR'
    ret = {'res': res, 'tim': tim, 'sta': sta}
    return ret


def main():
    print(http_check('https://www.baidu.com'))

    # print(ping_check('192.168.48.50'))

    print(tcp_check('192.168.48.10',1521))


if __name__ == '__main__':
    main()
