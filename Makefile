SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = dut.v
TOPLEVEL = dut
MODULE = test
include $(shell cocotb-config --makefiles)/Makefile.sim
