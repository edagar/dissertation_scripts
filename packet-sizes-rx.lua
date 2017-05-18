local mg        = require "moongen"
local dpdk		= require "dpdk"
local memory	= require "memory"
local device	= require "device"
local stats		= require "stats"
local timer		= require "timer"

--memory.enableCache()

local SRC_PORT		= 1234
local DST_PORT		= 319

local RUN_TIME = 15

function master(port1, port2)
	if not port1 or not port2 then
		return print("Usage: port1 port2")
	end
	local dev1 = device.config(port1)
	local dev2 = device.config(port2)

    for _, name in ipairs({ "rx_data", "tx_data" }) do
        local f = io.open(name, "w")
        f:close()
    end

	device.waitForLinks()
    for _, size in ipairs({60, 128, 256, 512, 1024, 1500}) do
		print("Running test for packet size = " .. size)
		local tx = mg.startTask("loadSlave", dev1:getTxQueue(0), size, "tx_data")
		local rx = mg.startTask("rxSlave", dev2:getRxQueue(0), size, "rx_data")
        mg.waitForTasks()
		if not mg.running() then
			break
		end
	end
    mg.waitForTasks()
end

local function fillUdpPacket(buf, len)
	buf:getUdpPacket():fill{
		ethSrc = "3C:FD:FE:05:C7:20",
		ethDst = "3C:FD:FE:03:04:A0",

		--ethSrc = "3C:FD:FE:05:94:C2",
		--ethDst = "3C:FD:FE:04:AB:02",

		ip4Src = "10.10.1.1",
		ip4Dst = "10.10.2.2",
		udpSrc = SRC_PORT,
		udpDst = DST_PORT,
		pktLength = len
	}
end

function dumper(ctr, size, filename)
    local f = io.open(filename, "a")
	local mpps, mbit, wireMbit, total, totalBytes = ctr:getStats()
    f:write(("%d,%.2f,%.2f\n"):format(size, mpps.avg, mpps.stdDev))
    f:close()

end

function loadSlave(queue, size, filename)
    local mem = memory.createMemPool(function(buf)
		fillUdpPacket(buf, size)
	end)

	local bufs = mem:bufArray()
	local ctr = stats:newDevTxCounter(queue.dev, "plain")
	local runtime = timer:new(RUN_TIME)
	while runtime:running() and mg.running() do
		bufs:alloc(size)
        --bufs:offloadUdpChecksums()
		queue:send(bufs)
		ctr:update()
	end
    dumper(ctr, size, filename)
	ctr:finalize()
end

function rxSlave(queue, size, filename)
	local bufs = memory.bufArray()
    --local ctr = stats:newManualRxCounter(queue.dev, "plain")
	local ctr = stats:newDevRxCounter(queue.dev, "plain")
	local runtime = timer:new(RUN_TIME)
	while runtime:running() and mg.running() do
		--local rx = queue:tryRecv(bufs, 100)
		bufs:freeAll()
		ctr:updateWithSize(rx, size)
        --ctr:update()
	end
    dumper(ctr, size, filename)
	ctr:finalize()
end

