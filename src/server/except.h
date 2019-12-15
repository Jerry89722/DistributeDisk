/*************************************************************************
	> File Name: except.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Sun 15 Dec 2019 09:56:41 AM CST
 ************************************************************************/
#ifndef __EXCEPT_H
#define __EXCEPT_H

#include <iostream>
#include <string>

using namespace std;

class UserException: public exception{
public:
	UserException()
	:m_msg("user info exception!")
	{}

	UserException(const string& msg)
	:m_msg("user info exception: ")
	{
		m_msg += msg;
		m_msg += "!";
	}

	~UserException(void) throw(){}

	const char* what(void) const throw()
	{
		return m_msg.c_str();
	}
private:
	string m_msg;
};


#endif //__EXCEPT_H
