#!/usr/bin/env python
# -*-coding:utf-8 -*-
import socket, struct, json
download_dir = r'D:\Python\python_learning\gd\code\part3\02网络编程\文件传输\client\download'
gd_client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
gd_client.connect(('127.0.0.1',8123))
while True:
    #1、发命令
    cmd = input('>>: ').strip() #get a.txt
    if not cmd:
        continue
    gd_client.send(cmd.encode('utf-8'))
    # 2、以写的方式打开一个新文件，接收服务端发来的文件的内容写入客户的新文件
    #第一步：先收报头的长度
    obj=gd_client.recv(4)
    header_size=struct.unpack('i',obj)[0]
    # 第二步：再收报头
    header_bytes = gd_client.recv(header_size)
    # 第三步：从报头中解析出对真实数据的描述信息
    header_json = header_bytes.decode('utf-8')
    header_dic = json.loads(header_json)
    '''
    header_dic = {
        'filename': filename, # 1.txt
        'file_size': os.path.getsize(r'%s\%s' % (share_dir, filename)) # 路径/1.txt
    }  
    '''
    total_size = header_dic['file_size']
    file_name = header_dic['filename']
    # 第四步：接收真实的数据
    with open(r'%s\%s'%(download_dir, file_name),'wb') as f:
        recv_size = 0
        while recv_size < total_size:
            line = gd_client.recv(1024)
            f.write(line)
            recv_size += len(line)
            print('总大小：%s  已下载大小：%s' % (total_size, recv_size))
            gd_client.close()
