import logging
import config
from logging.handlers import RotatingFileHandler


log_file = config.log_file
err_file = config.err_file
zabbix_file = config.zabbix_file

DEBUG = config.DEBUG

formatter = logging.Formatter(
#    fmt='%(asctime)s|%(name)s|%(levelname)s|Process:%(process)d|Thread:%(thread)d|%(message)s',
    fmt='%(asctime)s|%(levelname)s|Process:%(process)d|Thread:%(thread)d|%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(formatter)

err_handler = RotatingFileHandler(err_file, encoding='utf-8', maxBytes=1000000000, backupCount=3)
err_handler.setLevel(logging.ERROR)
err_handler.setFormatter(formatter)

log_handler = RotatingFileHandler(log_file, encoding='utf-8', maxBytes=1000000000, backupCount=3)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)

zabbix_handler = RotatingFileHandler(zabbix_file, encoding='utf-8', maxBytes=1000000000, backupCount=3)
zabbix_handler.setLevel(logging.DEBUG)
zabbix_handler.setFormatter(formatter)

log = logging.getLogger('log')

log.addHandler(err_handler)
log.addHandler(log_handler)

zbxlog = logging.getLogger('zabbix')
zbxlog.addHandler(zabbix_handler)
zbxlog.setLevel(logging.INFO)

if DEBUG:
    log.setLevel(logging.DEBUG)
    log.addHandler(stream)
else:
    log.setLevel(logging.INFO)
