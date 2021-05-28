# probe_tcp_connect
解析出url下所有地址，并对ip做tcp连接测试， 发送到zabbix。


#### zabbix 创建模板，添加自动发现规则。
#### 监控类型： zabbix 采集器
#### 默认有两个自动发现, 键值为：
###### 1、url.discovery
有两个监控项原型，分别是:  item[{#URL}:info]  与  item[{#URL}:ips],   数据类型都是 文本 或者 字符

###### 2、url.ip.discovery
有三个监控项原型, 分别是: 
item[{#URL}-{#IP}:error_info]   数据类型为 字符 或 文本。
item[{#URL}-{#IP}:health_check]   数字型
item[{#URL}-{#IP}:error_info]    字符 或 文本

