/*************************************************************************
	> File Name: clnt_thread.h
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月18日 星期五 20时22分48秒
 ************************************************************************/
#ifndef __CLNTTHREAD_H
#define __CLNTTHREAD_H

#include <list>
#include <deque>

#include <ev++.h>
#include <uuid/uuid.h>
#include <stdint.h>

using namespace std;

#define HW_BODY_BUF_MAX_LEN		1024
#define HW_HEADER_LEN			8

#define HW_TINY_BUF_LEN			32
#define HW_NORMAL_BUF_LEN		64
#define HW_BIG_BUF_LEN			128
#define HW_BIGGET_BUF_LEN		256

enum __HW_DATA_TYPE{
	_HW_DATA_TYPE_LOGIN,	// 0
	_HW_DATA_TYPE_HEARTBEAT,
	_HW_DATA_TYPE_ACK,
	_HW_DATA_TYPE_CMD,
	_HW_DATA_TYPE_LAST
};

enum __HW_CLNT_CMD{
	_HW_CMD_LS,
	_HW_CMD_RM,
	_HW_CMD_CP,
	_HW_CMD_MV,
	_HW_CMD_QUERY,
	_HW_CMD_LAST
};

class ClntThread;

struct ClntInfo{
	uint32_t& cid;
	ClntThread& clnt_thread;
	string name;
};

struct CmdInfo{
	uint32_t cid_from;
	string str_cmd;
};

class Payload{
public:
	Payload(int size = HW_BODY_BUF_MAX_LEN);
	uint8_t* m_buf;
	uint16_t m_offset;
	const uint16_t m_tlen;
private:
};

class ClntThread{
public:
	ClntThread(int fd);

	~ClntThread(void);
	
	void start(void);

	void work_start(void);

	void notify_me(void);
	
	void recv_handle(ev::io& watcher, int event);

	void event_handle(ev::async& watcher, int event);
	
	void timer_handle(ev::timer& watcher, int event);

	void cmd_parse(Payload& r_paylaod);

	int cmd_push_destination(Payload& payload, uint32_t cid);

	static int stream_recv(int fd, uint8_t* buf, int len, int retry_times);

	static list<ClntInfo> sm_clnt_list;

	deque<CmdInfo> m_deque_cmds;

private:
	Payload m_payload;
	uint8_t m_hbuf[HW_HEADER_LEN];
	int m_fd;
	uint32_t m_cid;
	pthread_t m_tid;
	ev::default_loop m_loop;
	ev::io m_recv_watcher;
	ev::async m_notify_watcher;
	ev::timer m_timer_watcher;

	static void* run(void* arg);

	int peer_clnt_verify(uint32_t cid, Payload& r_payload);
};

#endif // __CLNTTHREAD_H 

