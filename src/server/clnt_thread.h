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

#define HW_RECVED_EVENT		0
#define HW_SEND_EVENT		1

#define HW_BODY_BUF_MAX_LEN		1024
#define HW_HEADER_LEN			8

#define HW_TINY_BUF_LEN			32
#define HW_NORMAL_BUF_LEN		64
#define HW_BIG_BUF_LEN			128
#define HW_BIGGEST_BUF_LEN		256

enum __HW_DATA_TYPE{
	_HW_DATA_TYPE_LOGIN,		// 0
	_HW_DATA_TYPE_HEARTBEAT,	// 1
	_HW_DATA_TYPE_ACK,			// 2
	_HW_DATA_TYPE_CMD,			// 3
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

struct InteractiveData{
	ClntThread& clnt_from;
	string data_str;
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

	void notify_it(int which);
	
	void recv_handle(ev::io& watcher, int event);

	void request_event_handle(ev::async& watcher, int event);
	void reply_event_handle(ev::async& watcher, int event);
	
	void timer_handle(ev::timer& watcher, int event);

	void thread_work(void);
	void reply_thread(void);

	int request_push_destination(Payload& payload, uint32_t cid);

	static int stream_recv(int fd, uint8_t* buf, int len, int retry_times);

	static int stream_send(int fd, uint8_t* buf, int len, int retry_times);

	static list<ClntThread*> sm_clnt_list;

	deque<InteractiveData> m_deque_cmds;
	deque<InteractiveData> m_deque_results;

private:
	Payload m_payload_request;

	Payload m_payload_reply;

	uint8_t m_hbuf[HW_HEADER_LEN];
	int m_fd;
	uint32_t m_cid;
	string m_name;
	pthread_t m_tid;
	pthread_t m_request_tid;
	pthread_t m_reply_tid;
	pthread_mutex_t m_event_lock;
	
	ev::dynamic_loop m_loop;
	ev::io m_recv_watcher;
	ev::async m_req_watcher;
	ev::async m_rep_watcher;
	ev::timer m_timer_watcher;

	static void* run(void* arg);
	static void* request_handle_thread(void* arg);
	static void* reply_handle_thread(void* arg);

	int peer_clnt_verify(uint32_t cid, Payload& r_payload);
};

#endif // __CLNTTHREAD_H 

