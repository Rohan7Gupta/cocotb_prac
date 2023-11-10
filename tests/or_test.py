import cocotb
from cocotb.triggers import Timer, RisingEdge


@cocotb.test()
async def or_test(dut):
    a = (0, 0, 1, 1)
    b = (0, 1, 0, 1)
    y = (0, 1, 1, 1)

    for i in range(4):
        dut.a.value = a[i] #assignment of a and b at 0 time
        dut.b.value = b[i]
        await Timer(1, 'ns')# a and b might have different data rate
        #and may come at different times, so we ait for both to be ready
        assert dut.y.value == y[i], f"Error at iteration {i}"
