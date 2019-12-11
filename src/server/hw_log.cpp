/*************************************************************************
	> File Name: hw_log.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Wed 11 Dec 2019 07:41:54 PM CST
 ************************************************************************/

#include "hw_log.h"
void hw_hex_dump(char* pre, uint8_t* data_stream, int len)
{
	stringstream ss;
	
	for(int i = 0; i < len; ++i){
	
		ss << hex << setw(2) << setfill('0') << (unsigned int)(unsigned char)data_stream[i];
	}

	cout << pre << ": [" << ss.str() << "]" << endl;
}

