/*************************************************************************
	> File Name: clnt_thread.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月19日 星期六 16时47分15秒
 ************************************************************************/

#include <iostream>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include "cJSON.h"

#include "clnt_thread.h"

using namespace std;

list<ClntThread*> ClntThread::sm_clnt_list;

/**********************payload*********************/
Payload::Payload(ClntThread& clnt_from, int size)
:m_pclnt_from(&clnt_from), m_offset(0), m_tlen(size)
{
	m_buf = new uint8_t[m_tlen];
}

Payload::Payload(const Payload& payload)
:m_pclnt_from(payload.m_pclnt_from), m_offset(payload.m_offset), m_tlen(payload.m_offset)
{
	m_buf = new uint8_t[m_tlen];

	memcpy(m_buf, payload.m_buf, m_offset);
}

Payload::~Payload()
{
	delete m_buf;
}

/**********************payload*********************/

ClntThread::ClntThread(int fd)
:m_payload_request(*this), m_fd(fd)
{
	m_sbuf = new uint8_t[HW_SEND_BUF_LEN];

	m_recv_watcher.set(m_fd, ev::READ);
	m_recv_watcher.set(m_loop);
	m_recv_watcher.set<ClntThread, &ClntThread::recv_handle>(this);
	m_recv_watcher.start();

	m_req_watcher.set<ClntThread, &ClntThread::request_event_handle>(this);
	m_req_watcher.set(m_loop);
	m_req_watcher.start();

	m_timer_watcher.set(10.0, 60.0);
	m_timer_watcher.set(m_loop);
	m_timer_watcher.set<ClntThread, &ClntThread::timer_handle>(this);
	m_timer_watcher.start();
}

ClntThread::~ClntThread()
{
	m_timer_watcher.stop();
	
	m_req_watcher.stop();
	
	m_req_watcher.stop();
	
	m_recv_watcher.stop();
	
	m_loop.break_loop();
	
	close(m_fd);
	
	pthread_cancel(m_request_tid);
	
	pthread_cancel(m_tid);
}

void ClntThread::start(void)
{
	pthread_create(&m_tid, NULL, work_thread, this);

	/* use to handle clnt request, create here and not exit util clnt close, 
	 * in case create this thread frequently */
	pthread_create(&m_request_tid, NULL, request_handle_thread, this);
}

void* ClntThread::work_thread(void* arg)
{
	ClntThread* p_clnt = (ClntThread*) arg;

	p_clnt->work_start();

	return NULL;
}

void ClntThread::work_start(void)
{
	cout << "a client connection founded" << endl;
	
	while(1){
		m_loop.run(0);
		cout << "loop done" << endl;
	}
}

int ClntThread::peer_clnt_verify(Payload& r_payload, uint32_t cid)
{
	if(r_payload.m_offset < 1){

		cout << "clnt info verify failed, recved payload size abnormal" << endl;

		return -1;
	}
	
	m_cid = cid;

	m_name = string((char*)(r_payload.m_buf), r_payload.m_offset);

	sm_clnt_list.push_back(this);

	list<ClntThread*>::iterator it;

	Payload pld = Payload(*this, HW_NORMAL_BUF_LEN);

	cJSON* root = cJSON_CreateArray();

	for(it = sm_clnt_list.begin(); it != sm_clnt_list.end(); ++it){

		if((*it)->m_cid != cid){

			cJSON* clnt_node = cJSON_CreateObject();

			cJSON_AddStringToObject(clnt_node, "name", (*it)->m_name.c_str());

			cJSON_AddNumberToObject(clnt_node, "cid", (*it)->m_cid);

			cJSON_AddItemToArray(root, clnt_node);
		}
	}

	if(cJSON_GetArraySize(root) > 0){

		char* s = cJSON_PrintUnformatted(root);

		memcpy(pld.m_buf, s, strlen(s));

		pld.m_offset = strlen(s);

		cout << "clnts info: " << s << endl;

		free(s);
	}

	cJSON_Delete(root);


	if(strlen((char*)pld.m_buf) > 0){

		cout << (char*)pld.m_buf << endl;

		m_deque_cmds.push_back(pld);

		notify_it(HW_RECVED_EVENT);
	}

	return 0;
}

int ClntThread::stream_send(int fd, uint8_t* buf, int len, int retry_times)
{
	
	int t_len = 0, ret = 0, i;
	
	int n = (retry_times <= 0 ? 1: retry_times);

	for(i = 0; i < n; ++i){
		
		ret = send(fd, buf + t_len, len - t_len, 0);
		
		if(ret == 0){
			// connection is closed
			
			cout << "connection closed when send" << endl;
			
			return 0;

		}else if(ret < 0){
			// local error cause recv failed
			
			cout << "send failed because of local error" << endl;

			return -1;

		}else if(ret <= len){
			
			t_len += ret;
			
			if(t_len == len){

				break;

			}else if(t_len < len){
				
				usleep(50000);  // n * 10ms

				continue;
			}else if(t_len > len){

				cout << "send abnormal 1" << endl;

				return -1;
			}
		}else{
			
			cout << "send abnormal 2" << endl;

			return -1;
		}
	}

	return t_len;

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

		delete this;
		
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
	m_payload_request.m_type = type;

	if(size > m_payload_request.m_tlen){

		cout << "payload data too long" << endl;
		
		return ;
	}

	m_payload_request.m_offset = 0;
	bzero(m_payload_request.m_buf, m_payload_request.m_tlen);

	len = stream_recv(m_fd, m_payload_request.m_buf, size, 0);
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
		
		cout << "body recved, content: " << m_payload_request.m_buf << endl;
		
		m_payload_request.m_offset = len;
	}

	switch(type){
	case _HW_DATA_TYPE_LOGIN:
		
		peer_clnt_verify(m_payload_request, cid);
		
		break;
	case _HW_DATA_TYPE_HEARTBEAT:
		
		break;
	case _HW_DATA_TYPE_ACK:
		
		break;
	case _HW_DATA_TYPE_CMD:

		request_push_destination(m_payload_request, cid);
		
		break;
	default:
		
		break;
	}
}

void ClntThread::notify_it(int which)
{
	if(which == HW_RECVED_EVENT){

		m_req_watcher.send();
	}
}

int ClntThread::request_push_destination(Payload& payload, uint32_t cid) // des cid
{
	list<ClntThread*>::iterator it;
	
	cout << "request cid: " << cid << endl;

	for(it = sm_clnt_list.begin(); it != sm_clnt_list.end(); ++it){
		
		cout << "traverse cid: " << (*it)->m_cid << endl;

		if((*it)->m_cid == cid){

			Payload pld = payload;

			(*it)->m_deque_cmds.push_back(pld);
			
			(*it)->notify_it(HW_RECVED_EVENT);  // will change to dest client thread
														  //
			break;										//
		}											  //
	}												//
												  //
	return 0;									//
}											  //
											//
/*										  |/_
 * this event was triggled by another clnt_thread
 * */
void ClntThread::request_event_handle(ev::async& watcher, int event)
{
	cout << "event handle" << endl;

	if(&watcher == &m_req_watcher){
		
		cout << "request event handle, to id: " << m_request_tid << endl;

		pthread_kill(m_request_tid, SIGALRM);
	}
}

void* ClntThread::request_handle_thread(void* arg)
{
	ClntThread* pclnt = (ClntThread*)arg;
	
	signal(SIGALRM, sig_skip);

	pclnt->request_thread();

	return NULL;
}

void ClntThread::request_thread(void)
{
	int ret = 0;

	while(1){
		
		cout << "thread work start waiting ..., tid: " << m_request_tid << endl;

		pause();

		cout << "request handle work start" << endl;

		Payload req_pld = m_deque_cmds[0];
		
		m_deque_cmds.pop_front();

		cout << "cid_from: " << req_pld.m_pclnt_from->m_cid << endl;

		ret = pack(req_pld);

		ret = stream_send(m_fd, m_sbuf, 8 + req_pld.m_offset, 0);

	}
}


void ClntThread::timer_handle(ev::timer& watcher, int event)
{
	cout << "timer handle" << endl;
}

int ClntThread::pack(Payload& payload)
{
	uint8_t* p = m_sbuf;
	*(uint16_t*)p = payload.m_offset;
	p += 2;

	*(uint16_t*)p = payload.m_type;
	p += 2;

	*(uint32_t*)p = payload.m_pclnt_from->m_cid;
	p += 4;

	memcpy(p, payload.m_buf, payload.m_offset);

	return 0;
}

