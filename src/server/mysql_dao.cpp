/*************************************************************************
	> File Name: src/mysql_dao.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: Mon 07 Jan 2019 09:13:39 PM CST
 ************************************************************************/

#include <stdio.h>

#include <sstream>

#include <mysql_dao.h>

MysqlDao::MysqlDao(string user, 
		string password, 
		string db_name, 
		string charset, 
		string host)
:m_cursel_row(0)
{
	
	cout << __func__ << endl;

	m_pconn = new mysqlpp::Connection(false);

	m_res.clear();

	if(db_connect(user, password, db_name, charset, host) == false){

		m_conn_status = _STATUS_DISCONNECT;

		delete this;
	}else{
		
		m_conn_status = _STATUS_CONNECT;
	}

}

MysqlDao::~MysqlDao()
{
	
	cout << "destructor: " << __func__ << endl;

	m_pconn->disconnect();

	delete m_pconn;
}

bool MysqlDao::db_connect(string user, string passwd, string db_name, string charset, string host)
{
	if(!m_pconn->set_option(new mysqlpp::SetCharsetNameOption(charset.c_str()))){

		cout << "set charset failed" << endl;

		return false;
	}

	if(!m_pconn->set_option(new mysqlpp::ReconnectOption(true))){

		cout << "set reconnect failed" << endl;

		return false;
	}

	if(m_pconn->connect(db_name.c_str(), host.c_str(), user.c_str(), passwd.c_str()) == false){

		cout << "connect db failed" << endl;

		return false;
	}

	cout << "connect successfull" << endl;

	return true;
}

bool MysqlDao::exec_sql(const char* sql)
{
	cout << __func__ << endl;

	mysqlpp::Query  query = m_pconn->query();

	string str = sql;

	if (query.exec(str) == false){

		cout << str << " exec failed" << endl;

		return false;
	}

	cout << "exec success: " << str << endl;

	return true;
}

// 执行有返回结果的查询
bool MysqlDao::query_sql(const char* sql)
{
	mysqlpp::Query query = m_pconn->query();

	// 将sql语句执行，查询到的结果在query.store()里
	query << sql;

	// 将结果赋值给结果对象
	m_res.clear();
	m_cursel_row = 0;

	m_res = query.store();

	cout << "res num: " << m_res.num_rows() << endl;

	return true;
}

char* MysqlDao::string_lower(const char* pstr, char* out, int length)
{
	if( length == -1 )
		length = (int)strlen(pstr);
	int i;
	for(i = 0;i < length;i ++ ){
		out[i] = tolower(pstr[i]);
	}
	out[i] = 0; 
	return out;
}

bool MysqlDao::find_field_name(const char* field)
{
	int col = m_res.num_fields();

	char newfield[512];
	int i;
	for (i = 0; i < col; ++i){
		memset(newfield, 0, 512);
		string str = m_res.field_name(i);
		string_lower(field, newfield);
		if(str == newfield){
			return true;
		}
	}

	return false;
}

int MysqlDao::get_int_field(int field, int null_val)
{
	if(m_res.empty() || field + 1 > m_res.num_fields() || m_res.num_rows() == 0){
		cout << "no valid value" << endl;
		return null_val;
	}

	return (int)m_res[m_cursel_row][field];
}

int MysqlDao::get_int_field(const char* field, int null_val)
{
	if(m_res.empty() || 0 == m_res.num_rows() || find_field_name(field) == false){
		cout << "no valid value" << endl;
		return null_val;
	}

	return m_res[m_cursel_row][field];
}

const char* MysqlDao::get_string_field(int field, const char* null_val)
{
	if ( m_res.empty() || field + 1 > m_res.num_fields() || 0 == m_res.num_rows()){
		return null_val;
	}
	return m_res[m_cursel_row][field];
}

bool MysqlDao::eof()
{
	if( m_cursel_row >= m_res.size()) 
		return true;

	return false;
}

const char* MysqlDao::get_string_field(const char* field, const char* null_val)
{
	if(m_res.empty() || NULL == field || 0 == m_res.num_rows() || find_field_name(field) == false){
		return null_val;
	}
	return m_res[m_cursel_row][field];
}

void MysqlDao::next_row()
{
	if(m_res.empty())
		return;

	m_cursel_row++;
}


void MysqlDao::free_res()
{
	m_res.clear();
}


unsigned int MysqlDao::num_row()
{
	if (m_res.empty()){
		return 0;
	}

	return m_res.num_rows();
}


unsigned int MysqlDao::num_col()
{
	if (m_res.empty()){
		return 0;
	}

	return m_res.num_fields();
}

#if 0
int MysqlDao::sql_opt(AppInfo& app_info)
{
	static char sql[SQL_MAX_LEN];
	bzero(sql, SQL_MAX_LEN);
	string pre_path = "/oapps/";
	switch(app_info.status){
		case ST_CHK:
			snprintf(sql, SQL_MAX_LEN, INSERT_NEW_APP_RECORD,
					app_info.user_id,
					app_info.app_id,
					app_info.status);
			cout << "sql: " << sql << endl;
			exec_sql(sql);
			cout << "sql exec done" << endl;
			break;
		case ST_DOWNLOAD_WAITING:
		case ST_UPDATE_DOWNLOAD_WAITING:
			snprintf(sql, SQL_MAX_LEN, UPDATE_APP_INFO, 
					app_info.name.c_str(),
					app_info.package_name.c_str(),
					app_info.version.c_str(),
					app_info.version_id,
					app_info.category,
					app_info.status,
					app_info.file_md5.c_str(),
					app_info.file_size,
					app_info.publish_time.c_str(),
					app_info.manage_for_admin,
					app_info.use_for_admin,
					app_info.type.c_str(),
					app_info.device_type,
					app_info.declaration.c_str(),
					app_info.file_url.c_str(),
					app_info.icon_url.c_str(),
					(pre_path + app_info.package_name + app_info.phone_path).c_str(),
					(pre_path + app_info.package_name + app_info.pad_path).c_str(),
					(pre_path + app_info.package_name + app_info.pc_path).c_str(),
					(pre_path + app_info.package_name + app_info.tv_path).c_str(),
					app_info.phone_size.c_str(),
					app_info.pad_size.c_str(),
					app_info.pc_size.c_str(),
					app_info.tv_size.c_str(),
					app_info.can_install,
					app_info.token.c_str(),
					(pre_path + app_info.package_name + "/images/").c_str(),
					app_info.icon_small.c_str(),
					app_info.icon_medium.c_str(),
					app_info.icon_big.c_str(),
					app_info.id);

			cout << "sql: " << sql << endl;
			exec_sql(sql);
			break;
		case ST_DOWNLOADING:
		case ST_INSTALL_WAITING:
		case ST_INSTALLING:
		case ST_UNINSTALLING:
		case ST_UNINSTALL_DONE:
		case ST_UPDATE_DOWNLOAD_PAUSE:
		case ST_DOWNLOAD_PAUSE:
		case ST_DOWNLOAD_CANCEL:
		case ST_UPDATE_DOWNLOAD_CANCEL:
			snprintf(sql, SQL_MAX_LEN, UPDATE_APP_STATUS, 
					app_info.status, 
					app_info.timestamp,
					app_info.id);
			cout << "sql: " << sql << endl;
			exec_sql(sql);
			break;
		case ST_INSTALL_DONE:
		case ST_UPDATE_DONE:
			snprintf(sql, SQL_MAX_LEN, UPDATE_APP_INSTALL_INFO, 
					(app_info.install_path).c_str(),
					app_info.install_time.c_str(),
					app_info.timestamp,
					app_info.icon_path.c_str(),
					app_info.icon_small.c_str(),
					app_info.icon_medium.c_str(),
					app_info.icon_big.c_str(),
					app_info.status,
					app_info.id);
			cout << "sql: " << sql << endl;
			exec_sql(sql);
			break;
		case ST_INSTALL_CHK_ERR:
		case ST_UPDATE_CHK_ERR:
		case ST_INSTALL_DOWNLOAD_ERR:
		case ST_UPDATE_DOWNLOAD_ERR:
		case ST_INSTALL_ERR:
		case ST_UNINSTALL_ERR:
		case ST_UPDATE_ERR:
			snprintf(sql, SQL_MAX_LEN, UPDATE_APP_ERROR_INFO, 
					app_info.status,
					app_info.user_id,
					app_info.app_id);
			cout << "sql: " << sql << endl;
			exec_sql(sql);
			break;
		case ST_UPDATE_VERSION_INFO:
			snprintf(sql, SQL_MAX_LEN, UPDATE_APP_VERSION_INFO, 
					app_info.new_version_id,
					app_info.app_id);
			cout << "sql: " << sql << endl;
			exec_sql(sql);
			break;

	}

	return 0;
}

char* MysqlDao::list_sql_sentence_gen(int type)
{
	ostringstream status;

	status.str("");

	switch(type){
	case _CHK_INSTALLING_LIST:
		status << ST_DOWNLOAD_WAITING << "," << 
			ST_DOWNLOADING << "," << 
			ST_INSTALL_WAITING << "," << 
			ST_INSTALLING << "," << 
			ST_DOWNLOAD_PAUSE << "," << 
			ST_INSTALL_DONE << "," << 
			ST_INSTALL_DOWNLOAD_ERR << "," << 
			ST_INSTALL_CHK_ERR ;

		break;
	case _CHK_INSTALLED_LIST:

		status << ST_INSTALL_DONE;

		break;
	case _CHK_UPDATING_LIST:

		status << ST_UPDATE_DOWNLOAD_WAITING << "," << 
			ST_UPDATE_DOWNLOADING << "," << 
			ST_UPDATE_WAITING << "," << 
			ST_UPDATE_DONE << "," << 
			ST_UPDATING << "," << 
			ST_UPDATE_DOWNLOAD_PAUSE << "," << 
			ST_UPDATE_DOWNLOAD_ERR << "," << 
			ST_UPDATE_CHK_ERR ;
		break;
	case _CHK_UPDATED_LIST:
		
		status << ST_UPDATE_DONE;
		
		break;
	case _CHK_REMOVING_LIST:

		status << ST_UNINSTALLING;

		break;
	case _CHK_REMOVED_LIST:
	
		status << ST_UNINSTALL_DONE;

		break;
	}
	
	static char sql[256];
	
	snprintf(sql, sizeof(sql), "%s", status.str().c_str());

	return sql;

}

int MysqlDao::sql_chk(int type, TaskInfo& task_info, int app_id)
{
	static char sql[SQL_MAX_LEN];
	
	m_cursel_row = 0;

	bzero(sql, SQL_MAX_LEN);

	switch(type){
		case _CHK_MAINID:
			
			snprintf(sql, SQL_MAX_LEN, CHK_APP_MAINID, task_info.user_id, app_id);

			break;
		case _CHK_DOWNLOADING_NUMS:

			snprintf(sql, SQL_MAX_LEN, COUNT_APP_STATUS, ST_DOWNLOADING, task_info.user_id);

			break;
		case _CHK_INSTALLING_NUMS:

			snprintf(sql, SQL_MAX_LEN, COUNT_APP_STATUS, ST_INSTALLING, task_info.user_id);

			break;
		case _CHK_INSTALLING_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_INSTALLED_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_UPDATING_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_UPDATED_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_REMOVING_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_REMOVED_LIST:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_LIST, task_info.user_id, list_sql_sentence_gen(type));

			break;
		case _CHK_INSTALL_INFO:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_INSTALL_INFO, task_info.user_id, app_id);

			break;
		case _CHK_IS_INSTALLED:

			snprintf(sql, SQL_MAX_LEN, CHK_APP_IS_INSTALLED, task_info.user_id, app_id);

			break;
		case _CHK_ALL_INSTALLED_APPID:

			snprintf(sql, SQL_MAX_LEN, CHK_ALL_INSTALLED_APPID);

			break;
		case _CHK_APPINFO_FOR_UPDATE:

			snprintf(sql, SQL_MAX_LEN, CHK_APPINFO_FOR_UPDATE);

			break;
		case _CHK_ALL_APP_INFO:

			snprintf(sql, SQL_MAX_LEN, CHK_ALL_APP_INFO);

			break;

		default:
			break;
	}

	cout << "sql: " << sql << endl;

	query_sql(sql);

	return 0;
}
#endif 
