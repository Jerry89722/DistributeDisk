/*************************************************************************
	> File Name: clnt_thread.cpp
	> Author: Jerry
	> Mail: zhangjie89722@163.com 
	> Created Time: 2019年10月19日 星期六 16时47分15秒
 ************************************************************************/

#include <iostream>

#include <stdlib.h>
#include <string.h>
// #include <strings.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include "clnt_thread.h"

using namespace std;

list<ClntThread*> ClntThread::sm_clnt_list;

Payload::Payload(int size)
:m_offset(0), m_tlen(size)
{
	m_buf = (uint8_t*)malloc(m_tlen);
}

ClntThread::ClntThread(int fd)
:m_payload_request(), m_payload_reply(HW_BODY_BUF_MAX_LEN + 8), m_fd(fd)
{

	m_recv_watcher.set(m_fd, ev::READ);

	m_recv_watcher.set<ClntThread, &ClntThread::recv_handle>(this);

	m_recv_watcher.start();

	m_req_watcher.set<ClntThread, &ClntThread::request_event_handle>(this);

	m_req_watcher.start();

	m_rep_watcher.set<ClntThread, &ClntThread::request_event_handle>(this);

	m_rep_watcher.start();

	m_timer_watcher.set(10.0, 60.0);

	m_timer_watcher.set<ClntThread, &ClntThread::timer_handle>(this);

	m_timer_watcher.start();
}

ClntThread::~ClntThread(void)
{
	
}

void ClntThread::start(void)
{
	pthread_create(&m_tid, NULL, run, this);

	pthread_create(&m_request_tid, NULL, request_handle_thread, this);

	pthread_create(&m_reply_tid, NULL, reply_handle_thread, this);
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
	
	while(1){
		m_loop.run(ev::ONCE);
		cout << "loop done" << endl;
	}
}

int ClntThread::peer_clnt_verify(uint32_t cid, Payload& r_payload)
{
	if(r_payload.m_offset < 1){

		cout << "clnt info verify failed, recved payload size abnormal" << endl;

		return -1;
	}
	
	m_cid = cid;

	m_name = string((char*)(r_payload.m_buf), r_payload.m_offset);

	sm_clnt_list.push_back(this);

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
		
		peer_clnt_verify(cid, m_payload_request);
		
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

	}else if(which == HW_SEND_EVENT){
		
		m_rep_watcher.send();
	}
}

int ClntThread::request_push_destination(Payload& payload, uint32_t cid) // des cid
{
	list<ClntThread*>::iterator it;
	
	for(it = sm_clnt_list.begin(); it != sm_clnt_list.end(); ++it){

		if((*it)->m_cid == cid){

			InteractiveData data = {
				.clnt_from = **it
			};

			data.data_str = string((char*)payload.m_buf);

			(*it)->m_deque_cmds.push_back(data);
			
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
		
		cout << "request event handle" << endl;

		pthread_kill(m_request_tid, SIGALRM);
	}else if(&watcher == &m_rep_watcher){
		
		cout << "reply event handle" << endl;

		pthread_kill(m_reply_tid, SIGALRM);
	}

}

void* ClntThread::request_handle_thread(void* arg)
{
	ClntThread* pclnt = (ClntThread*)arg;
	
	signal(SIGALRM, SIG_IGN);

	pclnt->thread_work();

	return NULL;
}

void ClntThread::thread_work(void)
{
	while(1){
		
		cout << "thread work start waiting ..." << endl;

		pause();

		InteractiveData data = m_deque_cmds[0];
		
		m_deque_cmds.pop_front();

		InteractiveData dest_data = {
			.clnt_from = *this
		};
		
		cout << "cid_from: " << data.clnt_from.m_cid << endl;
		// 1. send cmd to peer clnt
		
		// 2. recv result from peer clnt
		
		// 3. notify_it();
		dest_data.data_str = "cmd handle results";

		dest_data.clnt_from.m_deque_results.push_back(dest_data);

		data.clnt_from.notify_it(HW_SEND_EVENT);
	}
}

void* ClntThread::reply_handle_thread(void* arg)
{
	ClntThread* pclnt = (ClntThread*)arg;
	
	signal(SIGALRM, SIG_IGN);

	pclnt->reply_thread();

	return NULL;
}

void ClntThread::reply_thread(void)
{
	while(1){
		pause();
		
		InteractiveData data = m_deque_results[0];
		m_deque_results.pop_front();

		*(uint16_t*)m_payload_reply.m_buf = data.data_str.size();
		*(uint16_t*)(m_payload_reply.m_buf + 2) = _HW_CMD_LS;
		*(uint32_t*)(m_payload_reply.m_buf + 4) = data.clnt_from.m_cid;

		memcpy(m_payload_reply.m_buf + 8, data.data_str.c_str(), data.data_str.size());

		stream_send(m_fd, m_payload_reply.m_buf, 8 + data.data_str.size(), 0);
	}
}

void ClntThread::timer_handle(ev::timer& watcher, int event)
{
	cout << "timer handle" << endl;
}

