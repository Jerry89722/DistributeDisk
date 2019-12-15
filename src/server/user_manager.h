/*************************************************************************
	> File Name: user_manager.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Sun 15 Dec 2019 12:17:16 AM CST
 ************************************************************************/
#ifndef __USER_MANAGER_H
#define __USER_MANAGER_H

#include <iostream>
#include <list>

#include "mysql_dao.h"

using namespace std;

class ClntThread;

class UserInfo{
public:

	UserInfo(string& user_name)
	:user_name(user_name)
	{
	
	}

	bool operator==(UserInfo& ui)
	{
		if(ui.user_name == user_name){
			
			return true;
		}else{
			
			return false;
		}
	}

public:
	string user_name;
	list<ClntThread*> user_clnts;

private:
};

class UserManager{
public:
	UserManager();
	// ~UserManager();
	UserInfo& operator[](const string& name);
	bool login_info_check(const string& name, const string& passwd);

private:
	void user_list_gen();
	list<UserInfo> m_user_clnts;
	MysqlDao m_dao;
};

#endif //__USER_MANAGER_H
