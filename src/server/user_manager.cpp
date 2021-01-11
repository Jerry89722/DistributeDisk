/*************************************************************************
	> File Name: user_manager.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Sun 15 Dec 2019 12:17:24 AM CST
 ************************************************************************/

#include <stdio.h>

#include "user_manager.h"
#include "except.h"

UserManager::UserManager()
:m_dao()
{
	// select name from dds_user_info;
	user_list_gen();
}

UserInfo& UserManager::operator[](const string& name)
{
	list<UserInfo>::iterator it;
	
	for(it = m_user_clnts.begin(); it != m_user_clnts.end(); ++it){
		
		if(name == it->user_name){
			
			return *it;

		}
	}
	
	throw UserException("there is no the user's info in our db");
}

/* ---------------------------------------------------------------- */
bool UserManager::login_info_check(const string& name, const string& passwd)
{
	static char sql[SQL_MAX_LEN];
	
	bzero(sql, SQL_MAX_LEN);
	
	snprintf(sql, SQL_MAX_LEN, GET_PASSWD_BY_NAME, name.c_str());
	m_dao.query_sql(sql);
	
	string passwd_db = m_dao.get_string_field("password");
	
	cout << "passwd in db: " << passwd_db << endl;
	cout << "passwd recved: " << passwd << endl;

	if(passwd_db == passwd){
		
		return true;
	}else{

		return false;
	}
}

void UserManager::user_list_gen()
{
	m_dao.query_sql(USER_LIST_GET);

	for(;;){
	
		if(m_dao.eof()){

			break;
		}
		
		string name = string(m_dao.get_string_field("name"));
		
		m_dao.next_row();
		
		cout << "user add into list: " << name << endl;

		UserInfo user_info(name);

		m_user_clnts.push_back(user_info);
	}
}

