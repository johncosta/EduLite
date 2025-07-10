# backend/performance_testing/c_core/Makefile
CC = gcc
CFLAGS = -shared -fPIC -Wall -Wextra -O2 -std=c99
PYTHON_INCLUDES = $(shell python3-config --includes)
TARGETS = libperformance.so
PERF_SOURCES = performance_monitor.c

all: $(TARGETS)

libperformance.so: $(PERF_SOURCES)
	$(CC) $(CFLAGS) $(PYTHON_INCLUDES) -o libperformance.so $(PERF_SOURCES)

clean:
	rm -f $(TARGETS)

test: $(TARGETS)
	@echo "Running C library tests..."
	@python3 -c "import ctypes; lib = ctypes.CDLL('./libperformance.so'); print('✅ Library loads successfully')"

install: $(TARGETS)
	@echo "Installing performance library..."
	@cp libperformance.so ../python_bindings/

.PHONY: all clean test install