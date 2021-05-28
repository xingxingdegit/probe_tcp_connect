import config
import socket
import traceback
import datetime
from logger import log

'''
    health code:
        0: 不健康
        1: 健康
'''

def tcp_check(ip, port):
    conn_timeout = config.tcp_connect_timeout
    items = {'health_check': 0, 'connect_seconds': 0, 'error_info': 'null'}
    try:
        cc = socket.socket()
        cc.settimeout(conn_timeout)
        start = datetime.datetime.now()
        cc.connect((ip, port))
        end = datetime.datetime.now()
    except socket.timeout:
        log.warn('ip:{}|port:{}|timeout'.format(ip, port))
        items['error_info'] = 'ConnectTimeout'
    except Exception:
        log.error('ip:{}|port:{}|异常错误'.format(ip, port))
        log.error(traceback.format_exc())
        items['error_info'] = 'ExceptionError'
    else:
        items['health_check'] = 1
        items['connect_seconds'] = (end-start).total_seconds()
    finally:
        cc.close()
    
    return items
