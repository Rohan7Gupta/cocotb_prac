

import cocotb
from cocotb.triggers import Timer, RisingEdge,ReadOnly, NextTimeStep
from cocotb_bus.drivers import BusDriver

def sb_fn(actual_value): #callback fxn
    global expected_value
    assert actual_value == expected_value.pop(0), "Scoreboard Matching failed"

@cocotb.test()
async def ifc_test_demo(dut):
    global expected_value
    expected_value = []
    a = (0, 0, 1, 1)
    b = (0, 1, 0, 1)
    expected_value = [0, 1, 1, 1]
    #when defining reset we need to define both falling and rising edgs
    #always @ (poseedge clk or negedge clk)
    #to ensure that we enter this block whenever the reset occurs
    dut.RST_N.value=1
    await Timer(1,'ns')
    dut.RST_N.value=0
    await Timer(1,'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value =1
    #instantiating drivers
    adrv = InputDriver(dut,'a',dut.CLK)
    bdrv = InputDriver(dut,'b',dut.CLK)
    OutputDriver(dut, 'y', dut.CLK, sb_fn)#cb_fn -> callback function
    
    for i in range(4):
        # adrv(a[i])
        # bdrv(b[i])
        adrv.append(a[i])
        bdrv.append(b[i])
    while len(expected_value)>0:
            await(Timer(2,'ns'))
        
class InputDriver(BusDriver):
    _signals=['rdy','en','data']
    
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk)
        self.bus.en.value=0#Enable always driven
        self.clk=clk
        
    async def _driver_send(self,value,sync=True):
        if self.bus.rdy.value !=1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value=1
        self.bus.data.value=value
        await ReadOnly()#wait for end of delta delay cycle
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
        
class OutputDriver(BusDriver):
    _signals=['rdy','en','data']
    
    def __init__(self,dut,name,clk, sb_callback):
        BusDriver.__init__(self,dut,name,clk)
        self.bus.en.value=0 #Enable always driven
        self.clk=clk
        self.callback = sb_callback
        self.append(0)
        
    async def _driver_send(self, value, sync=True):
        while True: 
            if self.bus.rdy.value !=1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value=1
            #self.bus.data=value
            await ReadOnly() 
            self.callback(self.bus.data.value)#wait for end of delta delay cycle
            await RisingEdge(self.clk)
            self.bus.en.value = 0
            await NextTimeStep()
         