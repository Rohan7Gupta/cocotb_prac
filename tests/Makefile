SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/or_gate.v
VERILOG_SOURCES += $(PWD)/wrappers/or_test.v
VERILOG_SOURCES += $(PWD)/wrappers/ifc_test.v
VERILOG_SOURCES += $(PWD)/../hdl/ifc_or.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO1.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
all: or ifc
or:
	rm -rf sim_build
	$(MAKE) sim MODULE=or_test TOPLEVEL=or_gate
ifc:
	rm -rf sim_build
	$(MAKE) sim MODULE=ifc_test TOPLEVEL=ifc_test
ifc_demo_dist:
	rm -rf sim_build
	$(MAKE) sim MODULE=ifc_test_demo TOPLEVEL=ifc_test
ifc_demo_rand:
	rm -rf sim_build
	$(MAKE) sim MODULE=ifc_test_rn TOPLEVEL=ifc_test
or_wave:
	rm -rf sim_build
	$(MAKE) sim MODULE=or_test TOPLEVEL=or_test
coverage:
	rm -rf sim_build
	$(MAKE) sim MODULE=ifc_coverage TOPLEVEL=ifc_test
include $(shell cocotb-config --makefiles)/Makefile.sim
