#!/usr/bin/env python
# -*-coding:utf-8 -*-
import socket
import subprocess
import struct
import json
import os
share_dir = r'D:\Python\python_learning\gd\code\part3\02网络编程\文件传输\server\share'
gd_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gd_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
gd_server.bind(('127.0.0.1', 8123)) # 0-65535: 0-1024给操作系统使用
gd_server.listen(5)
while True:
  conn, client_addr = gd_server.accept()
  while True: # 通信循环
    try:
      # 1、收命令
      res = conn.recv(8096) # b'get 1.txt'
      if not res: break # 适用于linux操作系统
      # 2、解析命令，提取相应命令参数
      cmds = res.decode('utf-8').split() # ['get','1.txt']
      filename = cmds[1]
      # 3、以读的方式打开文件,读取文件内容发送给客户端
      # 第一步：制作固定长度的报头
      header_dic = {
        'filename': filename, # 1.txt
        'file_size':os.path.getsize(r'%s\%s'%(share_dir, filename)) # 路径/1.txt
      }
      header_json = json.dumps(header_dic)
      header_bytes = header_json.encode('utf-8')
      # 第二步：先发送报头的长度
      conn.send(struct.pack('i',len(header_bytes)))
      # 第三步:再发报头
      conn.send(header_bytes)
      # 第四步：再发送真实的数据
      with open('%s/%s'%(share_dir, filename),'rb') as f:
        for line in f:
          conn.send(line)
    except ConnectionResetError: # 适用于windows操作系统
      break
  conn.close()
  gd_server.close()
