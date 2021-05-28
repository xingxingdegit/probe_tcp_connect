#
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parent.parent / 'conf'))
from logger import log, zbxlog
from zabbix_sender import ZabbixSender
import queue
import threading
import time
import datetime
import config
import random
import traceback
import json
import socket
from health_check import tcp_check

# 如果需要发送给zabbix， 需要用队列， monitor函数里需要添加数据到队列，  以及main函数里启动发送数据给zabbix的线程。
send_zabbix_queue = queue.Queue(config.zabbix_quque_num)

#global_urls_ips = {}
# 存储url的ip信息
# {url: {ip1, ip2....}, url: {,}}
global_urls_ips = {}

# 存储写入文件的信息
# {url: {url-ip-health: 0|1, url-ip-second: int, url-ip-error: str, url-info: str]}
# url-ip-error: 显示错误信息， 如连接失败，超时
# url-info: 显示一般信息， 如域名解析的ip列表发生变更
global_monitor_data = {}


def monitor(url, ip):
    try:
        sleep_num = random.randint(0, config.random_walk * 100) / 100
        time.sleep(sleep_num)

        for i in range(3):
            return_item = tcp_check(ip, 443)
    
            all_data = {
                'monitor_data': return_item,
                'url': url,
                'ip': ip,
                # 通过这个判断生成的信息时候url级别还是ip级别. 如 url的ip列表发生变化，就是url级别的。
                'type': 'ip',   
            }
            global_monitor_data[url] = all_data
        
            try:
                send_zabbix_queue.put(all_data, block=False)
            except queue.Full:
                # 队列太小 or 发送监控给zabbix的过程出现问题
                log.error('send_zabbix_queue is full')
            # ---------------------
            log.debug('data: {}:  数据已采集'.format(all_data))
            seconds = return_item['connect_seconds']
            health = return_item['health_check']
            if (health == 1) and (seconds < 0.01):
                break
            else:
                if health == 1:
                    log.debug('url:{}|ip:{}|seconds:{}|connect_seconds > 10ms'.format(url, ip, seconds))
                else:
                    log.debug('url:{}|ip:{}|seconds:{}|error:{}'.format(url, ip, seconds, return_item['error_info']))
                time.sleep(5)

    except Exception:
        log.error(traceback.format_exc())

def get_url_ip():
    log.debug('func:get_url_ip|Beginning ...')
    log.debug('last global_urls_ips is {}'.format(global_urls_ips))

    local_urls_ips = {}
    for url in config.urls:
        ips = socket.getaddrinfo(url, None)
        for ip in ips:
            local_urls_ips.setdefault(url, set()).add(ip[-1][0])
        
    # 判断ip列表是否变化
    if global_urls_ips:
        for url in local_urls_ips:
            drop_ips = global_urls_ips[url] - local_urls_ips[url]
            add_ips = local_urls_ips[url] - global_urls_ips[url]
            url_ip_change = []
            url_info = 'null'
            if drop_ips:
                url_ip_change.append('drop_ips:{}'.format(', '.join(drop_ips)))
            if add_ips:
                url_ip_change.append('add_ips:{}'.format(', '.join(add_ips)))
            if url_ip_change:
                global_urls_ips[url] = local_urls_ips[url]
                url_info = 'url:{},info:{}'.format(url, '|'.join(url_ip_change))

            ips = ','.join(sorted(list(local_urls_ips[url])))
            item_data = {
                'ips': ips,
                'info': url_info,
            }
            # 因与url-ip的监控项命名规则不同，不能统一处理， 所以这个字典的格式可以与url-ip那个不一样。
            all_data = {
                'monitor_data': item_data,
                'url': url,
                # 通过这个判断生成的信息是url的还是ip的. 如 url的ip列表发生变化，就是url的。ip连接失败超时就是ip的。
                'type': 'url',
            }

            try:
                send_zabbix_queue.put(all_data, block=False)
                log.debug('func:get_url_ip|url_info:{}'.format(url_info))
                log.debug('func:get_url_ip|url_ips:{}'.format(ips))
            except queue.Full:
                # 队列太小 or 发送监控给zabbix的过程出现问题
                log.error('send_zabbix_queue is full')
    else:
        global_urls_ips.update(local_urls_ips)

    log.debug('func:get_url_ip|complete get url_ip|data:{}'.format(global_urls_ips))
    send_discover_to_zabbix()


def send_discover_to_zabbix():
    try:
        sender_discover = ZabbixSender(config.zabbix_server, config.zabbix_port)
        discover_url_ip_data = {'data': []}
        discover_url_data = {'data': []}
        for url, ips in global_urls_ips.items():
            for ip in ips:
                discover_url_ip_data['data'].append(
                    {
                        "{#URL}": url,
                        "{#IP}": ip,
                    }
                )
            discover_url_data['data'].append(
                {
                    "{#URL}": url,
                }
            )
            log.info(discover_url_ip_data)
            log.info(discover_url_data)
        if discover_url_ip_data['data']:
            sender_discover.AddData(config.zabbix_iterm_hostname, config.zabbix_discover_url_ip, json.dumps(discover_url_ip_data))
            sender_discover.AddData(config.zabbix_iterm_hostname, config.zabbix_discover_url, json.dumps(discover_url_data))
            discover_recv_data = sender_discover.Send()
            zbxlog.info(sender_discover.zbx_sender_data['data'])
            zbxlog.info(discover_recv_data)
        else:
            log.error('func:send_to_zabbix|discover_url_ip_data:{}|discover_url_ip_data is null'.format(discover_url_ip_data['data']))
    except Exception:
        log.error(traceback.format_exc())

def send_to_zabbix():
    '''
        发送监控信息到zabbix
    '''
    # 为了防止自动发现的监控项还没有同步到zabbix， 导致监控项发送失败。
    # 这里在刚开始的时候等待10秒
    time.sleep(10)
    while True:
        try:
            sender_item = ZabbixSender(config.zabbix_server, config.zabbix_port)
            log.info('send_zabbix_queue size is: {}'.format(send_zabbix_queue.qsize()))
            for number in range(config.zabbix_send_num):
                if number > 0:
                    try:
                        all_data = send_zabbix_queue.get(block=False)
                    except queue.Empty:
                        log.debug('send_zabbix_queue is empty')
                        break
                else:
                    all_data = send_zabbix_queue.get(block=True)
                    
                item_prefix_name = config.zabbix_item_prefix
                if all_data['type'] == 'ip':
                    item_middle_name = '{}-{}'.format(all_data['url'], all_data['ip'])
                elif all_data['type'] == 'url':
                    item_middle_name = all_data['url']
                else:
                    log.error('{}:判断item_name出错'.format(all_data))
                    continue

                monitor_data = all_data['monitor_data']
                for item_post_name, item_value in monitor_data.items():
                    item_key = '{}[{}:{}]'.format(item_prefix_name, item_middle_name, item_post_name)
                    sender_item.AddData(config.zabbix_iterm_hostname, item_key, item_value)
            iterm_recv_data = sender_item.Send()
            zbxlog.info(sender_item.zbx_sender_data['data'])
            zbxlog.info(iterm_recv_data)
        except Exception:
            log.error(traceback.format_exc())
            time.sleep(1)

def send_to_file():
    while True:
        try:
            time.sleep(config.check_interval)
            with open(config.save_monitor_path, 'w') as fd:
                json.dump(global_monitor_data, fd)
        except Exception:
            log.error(traceback.format_exc())
            time.sleep(1)

def main():
    # 启动发送数据到zabbix的线程
    send_zabbix_thread = threading.Thread(target=send_to_zabbix)
    send_zabbix_thread.setDaemon(True)
    send_zabbix_thread.start()
    # 写监控信息到文件的线程
    if config.send_to_file:
        send_file_thread = threading.Thread(target=send_to_file)
        send_file_thread.setDaemon(True)
        send_file_thread.start()

    # 用来获取部署信息的功能使用
    last_get_url_list = None

    while True:
        log.info('---------------------------------')
        # 获取域名ip信息
        if (last_get_url_list is None) or (
                datetime.datetime.now() - last_get_url_list
            ).seconds > config.check_url_list_interval:
            last_get_url_list = datetime.datetime.now()
            get_url_ip_thread = threading.Thread(target=get_url_ip)
            get_url_ip_thread.start()

        # 启动监控线程
        log.info('--------------------------')
        start_time = datetime.datetime.now()
        for url, ips in global_urls_ips.items():
            for ip in ips:
                thread1 = threading.Thread(target=monitor, args=(url, ip))
                thread1.start()
        end_time = datetime.datetime.now()
        log.info('total monitor secons: {}'.format((end_time - start_time).total_seconds()))

        time.sleep(config.check_interval)


if __name__ == '__main__':
    main()


