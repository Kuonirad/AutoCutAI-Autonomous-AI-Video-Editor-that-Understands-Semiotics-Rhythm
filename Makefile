CXX ?= g++
LLVM_CONFIG ?= llvm-config-15

CXXFLAGS ?= -O2
WTMM_LIBS := -lgsl -lgslcblas -lm
JNORM_FLAGS := $(shell $(LLVM_CONFIG) --cxxflags)
JNORM_LDFLAGS := $(shell $(LLVM_CONFIG) --ldflags --libs core irreader)

.PHONY: all native-tools clean

all: native-tools

native-tools: wtmm bb-extract jnorm

wtmm: wtmm.cpp
	$(CXX) $(CXXFLAGS) $< $(WTMM_LIBS) -o $@

bb-extract: bb-extract.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

jnorm: jnorm.cpp
	$(CXX) $(CXXFLAGS) $(JNORM_FLAGS) $< $(JNORM_LDFLAGS) -o $@

clean:
	rm -f wtmm bb-extract jnorm *.bc *.o
