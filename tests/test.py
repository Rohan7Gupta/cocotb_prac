import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock


async def reset_seq(dut):
    dut.RST_N.value = 1
    await Timer(1, "ns")
    dut.RST_N.value = 0
    await Timer(1, "ns")
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    pass


@cocotb.test()
async def test_case(dut):
    dut.EN_next.value = 0
    dut.EN_start.value = 0
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())
    cocotb.start_soon(reset_seq(dut))
    values = [1, 2, 3, 4, 5]
    results = []
    await Timer(10, "ns")
    await RisingEdge(dut.CLK)
    dut.EN_start.value = 1
    await RisingEdge(dut.CLK)
    dut.EN_start.value = 0
    for idx, v in enumerate(values):
        dut.EN_next.value = 1
        dut.next_k.value = v
        await RisingEdge(dut.CLK)
        results.append(dut.next.value.integer)
    cocotb.log.info(f"Output is {hex(sum(results))}")
