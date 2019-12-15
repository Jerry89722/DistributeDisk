/*************************************************************************
	> File Name: inc/mysql_dao.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Mon 07 Jan 2019 09:04:15 PM CST
 ************************************************************************/

#ifndef __MYSQL_DAO
#define __MYSQL_DAO

#include <iostream>

#include <mysql++/mysql++.h>

using namespace std;

#define SQL_MAX_LEN 1024

#define MYSQL_USER "root"
#define MYSQL_PASSWORD  "admin"
#define MYSQL_DB_NAME	"dds"	
#define	MYSQL_CHARSET	"utf8mb4"		
#define MYSQL_HOST		"127.0.0.1"		

#define GET_PASSWD_BY_NAME	"select password from dds_user_info where name='%s';"
#define USER_LIST_GET	"select name from dds_user_info;"

#if 0
#define INSERT_NEW_APP_RECORD "insert ignore into app_user set user_id=%d, app_id=%d, status=%d;"

//获取主键id
#define CHK_MAIN_ID "select id from app_user where app_id=%d and user_id=%d;"

//app详细信息入库
// 1. app详细信息查询失败
#define UPDATE_APP_ERROR_INFO "update app_user set status=%d where user_id=%d and app_id=%d;"

// 2. app cloud详细信息入库
#define UPDATE_APP_INFO "update app_user set name='%s',package_name='%s',version='%s',version_id=%d,category=%d,status=%d,file_md5='%s',file_size=%lld,publish_time='%s',manage_for_admin=%d,use_for_admin=%d,type='%s',device_type='%d',declaration='%s',file_url='%s',icon_url='%s',phone_path='%s',pad_path='%s',pc_path='%s',tv_path='%s',phone_size='%s',pad_size='%s',pc_size='%s',tv_size='%s',can_install=%d,token='%s', icon_path='%s',icon_small='%s',icon_medium='%s',icon_big='%s' where id=%d;"

//更改app安装状态
#define UPDATE_APP_STATUS "update app_user set status=%d,start_stamp=%lu where id=%d;"

// app安装信息入库
#define UPDATE_APP_INSTALL_INFO "update app_user set install_path='%s',install_time='%s',end_stamp=%lu,icon_path='%s',icon_small='%s',icon_medium='%s',icon_big='%s',status=%d where id=%d;"

#define UPDATE_APP_VERSION_INFO "update app_user set new_version_id=%d where app_id=%d;"

// 查询当前正在下载/正在安装的个数
#define COUNT_APP_STATUS "select count(status=%d) nums from app_user where user_id=%d;"

// 查询主键id
#define CHK_APP_MAINID "select id,status from app_user where user_id=%d and app_id=%d;"

// 正在安装状态列表查询
#define CHK_APP_LIST "select * from app_user where user_id=%d and status in(%s);"


//查询已安装app安装信息
#define CHK_APP_INSTALL_INFO "select install_path from app_user where user_id=%d and app_id=%d;"

//查询app是否是已经安装状态
#define CHK_APP_IS_INSTALLED "select status from app_user where user_id=%d and app_id=%d;"

//查询所有app_id并去重
#define CHK_ALL_INSTALLED_APPID "select distinct app_id from app_user where status=5 or status=25;"

//后台更新查询
#define CHK_APPINFO_FOR_UPDATE "select app_id,user_id,token,version_id from app_user where status=5 or status=25;"

//查询所有app
#define CHK_ALL_APP_INFO "select app_id,version_id,status from app_user where status != 0;"

enum _APP_STATUS{
	ST_CHK,
	ST_DOWNLOAD_WAITING = 1,
	ST_DOWNLOADING,
	ST_INSTALL_WAITING,
	ST_INSTALLING,
	ST_INSTALL_DONE,
	ST_DOWNLOAD_PAUSE,
	ST_DOWNLOAD_CANCEL,

	ST_UNINSTALLING = 11,
	ST_UNINSTALL_DONE,

	ST_UPDATE_DOWNLOAD_WAITING = 21, // 更新包等待下载
	ST_UPDATE_DOWNLOADING,           // 更新包下载中
	ST_UPDATE_WAITING,               // 等待更新
	ST_UPDATING,                     // 更新中
	ST_UPDATE_DONE,                  // 更新成功
	ST_UPDATE_DOWNLOAD_PAUSE,
	ST_UPDATE_DOWNLOAD_CANCEL,

	ST_UPDATE_VERSION_INFO = 31,        //此状态不入库, 仅用于区分数据库操作时动作

	ST_INSTALL_CHK_ERR = 101,
	ST_INSTALL_DOWNLOAD_ERR = 102,
	ST_INSTALL_ERR = 103,

	ST_UNINSTALL_ERR = 111,

	ST_UPDATE_CHK_ERR = 121,
	ST_UPDATE_DOWNLOAD_ERR = 122,
	ST_UPDATE_ERR = 123
};

enum _CHK_TYPE{
	_CHK_MAINID,
	_CHK_DOWNLOADING_NUMS,
	_CHK_INSTALLING_NUMS,
	_CHK_INSTALL_INFO,
	_CHK_INSTALLING_LIST,
	_CHK_INSTALLED_LIST,
	_CHK_UPDATING_LIST,
	_CHK_UPDATED_LIST,
	_CHK_REMOVING_LIST,
	_CHK_REMOVED_LIST,
	_CHK_IS_INSTALLED,
	_CHK_ALL_INSTALLED_APPID,
	_CHK_APPINFO_FOR_UPDATE,
	_CHK_ALL_APP_INFO,
	_CHK_TYPE_ALL
};

#endif 

enum MYSQL_CONNECTION_STATUS{
	_STATUS_DISCONNECT,
	_STATUS_CONNECT,
	_STATUS_ALL,
};

class MysqlDao{
public:
	MysqlDao(string user = MYSQL_USER, 
			string password = MYSQL_PASSWORD,
			string db_name = MYSQL_DB_NAME, 
			string charset = MYSQL_CHARSET, 
			string host = MYSQL_HOST);

	~MysqlDao();

	// int sql_opt(AppInfo& app_info);

	// int sql_chk(int type, TaskInfo& app_info, int app_id = 0);

	bool db_connect(string user, 
			string passwd, 
			string db_name, 
			string charset, 
			string host);

	bool find_field_name(const char* field);

	int get_int_field(int field, int null_val = 0);
	int get_int_field(const char* field, int null_val = 0);

	const char* get_string_field(int field, const char* null_val = "");
	const char* get_string_field(const char* field, const char* null_val = "");

	static char* string_lower(const char* pstr , char* out, int length = -1);

	// 一共查询到多少行数据
	unsigned int num_row();

	// 一共有多少列
	unsigned int num_col();

	// 判断是否是最后一行
	bool eof();

	// 将当前行数往下移动一行
	void next_row();

	// 释放资源
	void free_res();

	//  执行sql语句
	bool exec_sql(const char* sql);

	// 执行有返回结果的查询
	bool query_sql(const char* sql);

private:
	mysqlpp::Connection* m_pconn;
	
	mysqlpp::StoreQueryResult m_res;

	unsigned int m_cursel_row;
	
	int m_conn_status;

	// char* list_sql_sentence_gen(int type);

};

#endif //__MYSQL_DAO


/*
private:
	int insert();

	int update();

	int select();

	int m_conn_status;

 * */
