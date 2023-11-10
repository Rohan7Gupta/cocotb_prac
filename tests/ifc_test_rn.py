#test with random test

import cocotb
from cocotb.triggers import Timer, RisingEdge,ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
import os
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import random

def sb_fn(actual_value): #callback fxn
    global expected_value
    assert actual_value == expected_value.pop(0), "Scoreboard Matching failed"

@CoverPoint("top.a",#noqa F405
            xf=lambda x,y:x,
            bins=[0,1]
            )
@CoverPoint("top.b",#noqa F405
            xf=lambda x,y:y,
            bins=[0,1]
            )
@CoverCross("top.cross.ab",
            items = ["top.a",
                     "top.b"
                    ]
            )

def ab_cover(a, b):
    pass

@CoverPoint("top.prot.a.current",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverPoint("top.prot.a.previous",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverCross("top.cross.a_prot.cross",
            items=["top.prot.a.previous",
                   "top.prot.a.current"
                   ],
            ign_bins=[('Rdy', 'Idle')]
            )
def a_prot_cover(txn):
    pass

@cocotb.test()
async def ifc_test_demo(dut):
    global expected_value
    expected_value = []
    #a = (0, 0, 1, 1)
    #b = (0, 1, 0, 1)
    #expected_value = [0, 1, 1, 1]
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
    IO_Monitor(dut, 'a', dut.CLK, callback=a_prot_cover)
    bdrv = InputDriver(dut,'b',dut.CLK)
    OutputDriver(dut, 'y', dut.CLK, sb_fn)#cb_fn -> callback function
    
    for i in range(4):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        expected_value.append(a | b)
        adrv.append(a)
        bdrv.append(b)
        ab_cover(a,b)
    while len(expected_value)>0:
            await(Timer(2,'ns'))
            
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(
        os.getenv('RESULT_PATH', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)
        
class InputDriver(BusDriver):
    _signals=['rdy','en','data']
    
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk)
        self.bus.en.value=0#Enable always driven
        self.clk=clk
        
    async def _driver_send(self,value,sync=True):
        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        if self.bus.rdy.value !=1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value=1
        self.bus.data.value=value
        await ReadOnly()#wait for end of delta delay cycle
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
        
class IO_Monitor(BusMonitor):
    _signals = ['rdy', 'en', 'data']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        phases = {
            0: 'Idle',#both en and rdy are 0
            1: 'Rdy',#if en==, rdy=1
            3: 'Txn'#en=1, rdy=1 i.e. both ready and enable
            #en=1,rdy=0 not valid... enable not possible w/o ready
        }
        prev = 'Idle'
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn]

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
            for i in range(random.randint(0, 20)):
                await RisingEdge(self.clk)
            if self.bus.rdy.value !=1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value=1
            #self.bus.data=value
            await ReadOnly() 
            self.callback(self.bus.data.value)#wait for end of delta delay cycle
            await RisingEdge(self.clk)
            self.bus.en.value = 0
            await NextTimeStep()
         