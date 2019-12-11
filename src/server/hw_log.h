/*************************************************************************
	> File Name: hw_log.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Wed 11 Dec 2019 07:41:33 PM CST
 ************************************************************************/

#ifndef __HW_LOG_H
#define __HW_LOG_H
#include <iostream>
#include <sstream>
#include <iomanip>

#include <stdint.h>

using namespace std;

void hw_hex_dump(char* pre, uint8_t* data_stream, int len);
#endif //__HW_LOG_H
