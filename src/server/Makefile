PROJ   = server
OBJS   = main.o server.o server_socket.o user_manager.o clnt_thread.o cJSON.o hw_log.o mysql_dao.o
		 
CXX    = g++
RM     = rm -rf
CFLAGS = -c -Wall -I. -D_DEBUG -I/usr/include/mysql/
LIBS   = -lpthread -lev -lmysqlpp
$(PROJ): $(OBJS)
	$(CXX) $^ $(LIBS) -o $@
.cpp.o:
	$(CXX) $(CFLAGS) $^
clean:
	$(RM) $(PROJ) $(OBJS)

