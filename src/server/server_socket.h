/*************************************************************************
	> File Name: server_socket.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月18日 星期五 20时03分37秒
 ************************************************************************/

#ifndef __SERVER_SOCKET_H
#define __SERVER_SOCKET_H

#include <string>

using namespace std;

class ServerSocket{
public:
	ServerSocket(string ip, int port);

	void clntAccept(void);

private:
	int m_sockfd;
};

#endif //__SERVER_H
