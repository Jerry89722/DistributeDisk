PROJ   = server
OBJS   = main.o server.o server_socket.o clnt_thread.o 
		 
CXX    = g++
RM     = rm -rf
CFLAGS = -c -Wall -I. -D_DEBUG
LIBS   = -lpthread -lev
$(PROJ): $(OBJS)
	$(CXX) $^ $(LIBS) -o $@
.cpp.o:
	$(CXX) $(CFLAGS) $^
clean:
	$(RM) $(PROJ) $(OBJS)

