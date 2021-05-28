from pathlib import Path

basedir = Path(__file__).absolute().parent.parent

# Path type
log_file = basedir / 'log/access.log'
err_file = basedir / 'log/error.log'
zabbix_file = basedir / 'log/send_zabbix.log'

DEBUG = True

###########################

# 发起检查的间隔, 单位: 秒， 所有监控线程都发起以后，等待下次发起的时间。
check_interval = 60


# 为了避免突发大量请求，设置一个随机间隔, 单位：秒, 所有请求在0-#之间随机等待。
random_walk = 5

##########################

# 解析url ip的间隔。
check_url_list_interval = 180


urls = ['url1', 'url2'] # 不要加http前缀
# 下次检查部署列表的时候发现上次还没执行完，可能故障了，是否重新发起

########################

# 是否推送监控信息到zabbix, 推送信息的时间不固定，
# 由各个监控线程探测完毕以后推到队列，然后另一个线程获取并发送。
zabbix_server = ''  # zabbix server ip
zabbix_port = 10051
# 推送的监控项中的主机名, 也就是zabbix中添加的监控项在哪个主机下
zabbix_iterm_hostname = 'Zabbix server'
# zabbix自动发现监控项键值
zabbix_discover_url_ip = 'url.ip.discovery'
zabbix_discover_url = 'url.discovery'
# zabbix自动发现里宏的名字, 就是变量的名字。
#zabbix_discover_macro_name = 'URL-IP'
# zabbix监控项的前缀
zabbix_item_prefix = 'item'
# 因为需要实时发送给zabbix， 所以需要队列保存数, 数值根据监控的服务部署数量确定，不能那边还没有开始发送，这边就塞满了。
zabbix_quque_num = 300
# 一次性发送给zabbix的最大监控数量:
zabbix_send_num = 100

# 是否保存监控信息到文件, 每check_interval时间保存一次，这一次保存的可能是上一次探测的结果, 没有推送给zabbix的实时。
# 主要用于查看监控的一些细节信息， 用作调试。
send_to_file = True
save_monitor_path = basedir / 'tmp/monitor.html'

#########################

# 检查tcp接口的超时时间：秒, 支持浮点数
tcp_connect_timeout = 5













