/*************************************************************************
	> File Name: server.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月18日 星期五 23时43分13秒
 ************************************************************************/

#include <iostream>

#include "server.h"

using namespace std;
Server::Server(string ip, int port)
:m_socket(ip, port)
{
	cout << "Server construct" << endl;
}

void Server::start(void)
{
	m_socket.clntAccept();
}
