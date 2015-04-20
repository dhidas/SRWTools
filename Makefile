CC = g++
LD = g++
CFLAGS = -Wall -O3
LIBS =
INCLUDE = -Iinclude
OBJS  = $(patsubst src/%.cc,lib/%.o,$(wildcard src/*.cc))
EXECS = $(patsubst bin/%.cc,%,$(wildcard bin/*.cc))
EXEOBJS  = $(patsubst bin/%.cc,lib/%.o,$(wildcard bin/*.cc))


all: $(OBJS) $(EXEOBJS) $(EXECS)

lib/%.o : src/%.cc
	$(CC) -Wall $(CFLAGS) $(INCLUDE) -c $< -o $@

lib/%.o : bin/%.cc
	$(CC) -Wall $(CFLAGS) $(INCLUDE) -c $< -o $@


% : $(OBJS) lib/%.o
	$(LD) $(LIBS) $(OBJS) $(LINKDEFOBJ) lib/$@.o -o $@





clean:
	rm -f $(EXECS) lib/*.o
