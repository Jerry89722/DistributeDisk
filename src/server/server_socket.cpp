/*************************************************************************
	> File Name: server_socket.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月19日 星期六 16时39分47秒
 ************************************************************************/

#include <iostream>

#include <sys/types.h>
#include <sys/stat.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include "server_socket.h"
#include "clnt_thread.h"

using namespace std;

ServerSocket::ServerSocket(string ip, int port)
{
	cout << "server socket init start..." << endl;

	// 创建侦听套接字
	if ((m_sockfd = socket (AF_INET, SOCK_STREAM, 0)) == -1){
		
		cout << "socket create failed" << endl;

		return ;
	}

	// 设置套接字选项
	int on = 1;
	if (setsockopt (m_sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof (on)) == -1){
	
		cout << "socket opt set failed" << endl;

		return ;			
	}

	// 绑定地址和端口
	sockaddr_in addr;
	addr.sin_family = AF_INET;
	addr.sin_port = htons (port);
	addr.sin_addr.s_addr = ip.empty () ? INADDR_ANY : inet_addr (ip.c_str ());
	if (bind (m_sockfd, (sockaddr*)&addr, sizeof (addr)) == -1){

		cout << "socket bind failed" << endl;

		return ;
	}

	// 设置为侦听状态
	if (listen (m_sockfd, 1024) == -1){

		cout << "socket listen failed" << endl;

		return ;
	}

	cout << "server socket init done" << endl;
}

void ServerSocket::clntAccept(void)
{
	int fd = 0;
	for(;;){
		sockaddr_in addrcli;

		socklen_t addrlen = sizeof (addrcli);

		fd = accept (m_sockfd, (sockaddr*)&addrcli, &addrlen);
		if(fd < 0){

			continue;
		}
		cout << "new clnt thread" << endl;
		(new ClntThread(fd))->start();
	}
}

