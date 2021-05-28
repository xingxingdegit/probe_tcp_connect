# 从网上下载的脚本
import socket
import struct
import simplejson
class ZabbixSender:
        zbx_header = 'ZBXD'
        zbx_version = 1
        send_data = ''
        def __init__(self, server_host, server_port = 10051):
                self.zbx_sender_data = {'request': 'sender data', 'data': []}
                self.server_ip = socket.gethostbyname(server_host)
                self.server_port = server_port
        def AddData(self, host, key, value, clock = None):
                add_data = {'host': host, 'key': key, 'value': value}
                if clock != None:
                        add_data['clock'] = clock
                self.zbx_sender_data['data'].append(add_data)
                return self.zbx_sender_data
        def ClearData(self):
                self.zbx_sender_data['data'] = []
                return self.zbx_sender_data
        def __MakeSendData(self):
                zbx_sender_json = simplejson.dumps(self.zbx_sender_data, separators=(',', ':'), ensure_ascii=False)
                json_byte = len(zbx_sender_json)
                self.send_data = struct.pack(
                    "<4sBq" + str(json_byte) + "s", self.zbx_header.encode('utf-8'), self.zbx_version, json_byte, zbx_sender_json.encode('utf-8')
                )
        def Send(self):
                self.__MakeSendData()
                so = socket.socket()
                so.connect((self.server_ip, self.server_port))
                wobj = so.makefile('wb')
                wobj.write(self.send_data)
                wobj.close()
                robj = so.makefile('rb')
                recv_data = robj.read()
                robj.close()
                so.close()
                tmp_data = struct.unpack("<4sBq" + str(len(recv_data) - struct.calcsize("<4sBq")) + "s", recv_data)
                recv_json = simplejson.loads(tmp_data[3])
                return recv_json
