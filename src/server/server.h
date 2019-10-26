/*************************************************************************
	> File Name: server.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月18日 星期五 20时18分59秒
 ************************************************************************/

#ifndef __SERVER_H
#define __SERVER_H

#include "server_socket.h"

struct ClntInfo_t{
	pthread_t tid;
	string name;
	int fd;
}; 

class Server{
public:
	Server(string ip = "", int port = 9001);

	void start(void);
private:
	ServerSocket m_socket;
};

#endif //__SERVER_H

