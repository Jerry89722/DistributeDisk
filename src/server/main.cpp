/*************************************************************************
	> File Name: main.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月18日 星期五 23时35分32秒
 ************************************************************************/

#include <iostream>

#include "server.h"

using namespace std;


int main(int argc, char* argv[])
{

	Server server = Server();

	server.start();

	return 0;
}
