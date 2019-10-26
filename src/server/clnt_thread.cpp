/*************************************************************************
	> File Name: clnt_thread.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月19日 星期六 16时47分15秒
 ************************************************************************/

#include <iostream>

#include <stdlib.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include "clnt_thread.h"

using namespace std;

list<ClntInfo> ClntThread::sm_clnt_list;

Payload::Payload(int size)
:m_offset(0), m_tlen(size)
{
	m_buf = (uint8_t*)malloc(m_tlen);
}

ClntThread::ClntThread(int fd)
:m_payload(), m_fd(fd)
{
	m_recv_watcher.set(m_fd, ev::READ);

	m_recv_watcher.set<ClntThread, &ClntThread::recv_handle>(this);

	m_recv_watcher.start();

	m_notify_watcher.set<ClntThread, &ClntThread::event_handle>(this);

	m_notify_watcher.start();

	m_timer_watcher.set(1.0, 2.0);

	m_timer_watcher.set<ClntThread, &ClntThread::timer_handle>(this);

	m_timer_watcher.start(1.0, 2.0);
}

ClntThread::~ClntThread(void)
{
	
}

void ClntThread::start(void)
{
	pthread_create(&m_tid, NULL, run, this); 

	pthread_detach(m_tid);
}

void* ClntThread::run(void* arg)
{
	ClntThread* p_clnt = (ClntThread*) arg;

	p_clnt->work_start();

	return NULL;
}

void ClntThread::work_start(void)
{
	cout << "a client connection founded" << endl;

	m_loop.run(0);

	cout << "loop done" << endl;
}

int ClntThread::peer_clnt_verify(uint32_t cid, Payload& r_payload)
{
	if(r_payload.m_offset < 1){

		cout << "clnt info verify failed, recved payload size abnormal" << endl;

		return -1;
	}
	
	ClntInfo ci = {};

	ci.cid = cid;
	ci.name = string((char*)(r_payload.m_buf), r_payload.m_offset);

	sm_clnt_list.push_back(ci);

	return 0;
}

// static 
int ClntThread::stream_recv(int fd, uint8_t* buf, int len, int retry_times)
{
	int t_len = 0, ret = 0, i;
	
	int n = (retry_times <= 0 ? 1: retry_times);

	for(i = 0; i < n; ++i){
		
		ret = recv(fd, buf + t_len, len - t_len, 0);
		
		if(ret == 0){
			// connection is closed
			
			cout << "connection closed" << endl;
			
			return 0;

		}else if(ret < 0){
			// local error cause recv failed
			
			cout << "recv failed because of local error" << endl;

			return -1;

		}else if(ret <= len){
			
			t_len += ret;
			
			if(t_len == len){

				break;

			}else if(t_len < len){
				
				usleep(50000);  // n * 10ms

				continue;
			}else if(t_len > len){

				cout << "recv abnormal 1" << endl;

				return -1;
			}
		}else{
			
			cout << "recv abnormal 2" << endl;

			return -1;
		}
	}

	return t_len;
}

/*
 * header:
 *	len :	2bytes
 *	type:	2bytes
 *	cid :	4bytes
 *	body:	len bytes
 * */
void ClntThread::recv_handle(ev::io& watcher, int event)
{
	cout << "recv handler enter" << endl;

	bzero(m_hbuf, HW_HEADER_LEN);

	int len = stream_recv(m_fd, m_hbuf, HW_HEADER_LEN, 0);
	if(len == 0){
		
		cout << "connection closed when recving header" << endl;
		
		return ;
	}else if(len < 0){

		cout << "recv failed, local error happend when recving header" << endl;

		return ;
	}else if(len < HW_HEADER_LEN){

		cout << "header data recv overtime" << endl;
		
		return ;
	}else{
		
		cout << "header recv done: " << len << endl;
	}

	int size = *((uint16_t*)m_hbuf);
	int type = *((uint16_t*)(m_hbuf+2));
	int cid = *((uint16_t*)(m_hbuf+4));
	
	cout << "size: " << size << endl;
	cout << "type: " << type << endl;
	cout << "cid: " << cid << endl;

	if(size > m_payload.m_tlen){

		cout << "payload data too long" << endl;
		
		return ;
	}

	m_payload.m_offset = 0;
	bzero(m_payload.m_buf, m_payload.m_tlen);

	len = stream_recv(m_fd, m_payload.m_buf, size, 0);
	if(len == 0){
		
		cout << "connection closed when recving body" << endl;
		
		return ;
	}else if(len < 0){

		cout << "recv failed, local error happend when recving body" << endl;

		return ;
	}else if(len < size){

		cout << "body data recv overtime, recved len: " << len << endl;
		
		return ;
	}else{
		
		cout << "body recv done, content: " << m_payload.m_buf << endl;
		
		m_payload.m_offset = len;
	}

	switch(type){
	case _HW_DATA_TYPE_LOGIN:
		
		peer_clnt_verify(cid, m_payload);
		
		break;
	case _HW_DATA_TYPE_HEARTBEAT:
		
		break;
	case _HW_DATA_TYPE_ACK:
		
		break;
	case _HW_DATA_TYPE_CMD:
		
		break;
	default:
		
		break;
	}
}

void ClntThread::cmd_parse(Payload& r_payload)
{
	CmdInfo cmd_info = {};
	
	cmd_info.cmd = (__HW_CLNT_CMD)*(uint32_t*)r_payload.m_buf;
	
}

void ClntThread::event_handle(ev::async& watcher, int event)
{
	cout << "event handle" << endl;
}

void ClntThread::timer_handle(ev::timer& watcher, int event)
{
	cout << "timer handle" << endl;
}

