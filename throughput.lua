local mg     = require "moongen"
local memory = require "memory"
local device = require "device"
local ts     = require "timestamping"
local filter = require "filter"
local hist   = require "histogram"
local stats  = require "stats"
local timer  = require "timer"
local arp    = require "proto.arp"
local log    = require "log"
local dpdk   = require "dpdk"

local SRC_IP_BASE	= "10.0.0.10" -- actual address will be SRC_IP_BASE + random(0, flows)
local DST_IP		= "10.10.2.2"
local SRC_PORT		= 1234
local DST_PORT		= 319

local RUN_TIME = 20

function configure(parser)
	parser:description("Generates UDP traffic and measure latencies. Edit the source to modify constants like IPs.")
	parser:argument("txDev", "Device to transmit from."):convert(tonumber)
	parser:argument("rxDev", "Device to receive from."):convert(tonumber)
	parser:option("-r --rate", "Transmit rate in Mbit/s."):default(10000):convert(tonumber)
	parser:option("-f --flows", "Number of flows (randomized source IP)."):default(4):convert(tonumber)
	parser:option("-s --size", "Packet size."):default(60):convert(tonumber)
end

function master(args)
	txDev = device.config{port = args.txDev, rxQueues = 3, txQueues = 3}
	rxDev = device.config{port = args.rxDev, rxQueues = 3, txQueues = 3}
	device.waitForLinks()
	-- max 1kpps timestamping traffic timestamping
	-- rate will be somewhat off for high-latency links at low rates
	if args.rate > 0 then
		txDev:getTxQueue(0):setRate(args.rate - (args.size + 4) * 8 / 1000)
	end

    for _, name in ipairs({ "rx_data" }) do
        local f = io.open(name, "w")
        f:close()
    end

    for _, size in ipairs({60, 128, 256, 512, 1024, 1500}) do
		print("Running test for packet size = " .. size)
        mg.startTask("loadSlave", txDev:getTxQueue(0), rxDev, size, args.flows, "rx_data")
        mg.startTask("dumpSlave", rxDev:getRxQueue(0), size, "rx_data")
        mg.waitForTasks()
		if not mg.running() then
			break
		end
    end
	mg.waitForTasks()
end

function dumper(ctr, size, filename)
    local f = io.open(filename, "a")
	local mpps, mbit, wireMbit, total, totalBytes = ctr:getStats()
    f:write(("%d,%.2f,%.2f\n"):format(size, mpps.avg, mpps.stdDev))
    f:close()

end

local function fillUdpPacket(buf, len)
	buf:getUdpPacket():fill{
		ethSrc = "3C:FD:FE:05:94:C0",
		ethDst = "3C:FD:FE:04:DC:20",
		ip4Src = SRC_IP,
		ip4Dst = DST_IP,
		udpSrc = SRC_PORT,
		udpDst = DST_PORT,
		pktLength = len
	}
end

function dumpSlave(queue, size, dumpfile)
	local bufs = memory.bufArray()
	local pktCtr = stats:newPktRxCounter("Packets counted", "plain")
	local runtime = timer:new(RUN_TIME)

	while runtime:running() and mg.running() do
		local rx = queue:tryRecv(bufs, 100)
		for i = 1, rx do
			local buf = bufs[i]
			pktCtr:countPacket(buf)
		end
		bufs:free(rx)
		pktCtr:update()
	end
    dumper(pktCtr, size, dumpfile)
	pktCtr:finalize()
end

function loadSlave(queue, rxDev, size, flows, dumpfile)
	local mempool = memory.createMemPool(function(buf)
		fillUdpPacket(buf, size)
	end)
	local bufs = mempool:bufArray()
	local counter = 0
	local txCtr = stats:newDevTxCounter(queue, "plain")
	--local rxCtr = stats:newDevRxCounter(rxDev, "plain")

	local baseIP = parseIPAddress(SRC_IP_BASE)
	local runtime = timer:new(RUN_TIME)

	while runtime:running() and mg.running() do
		bufs:alloc(size)
		for i, buf in ipairs(bufs) do
			local pkt = buf:getUdpPacket()
			pkt.ip4.src:set(baseIP + counter)
			counter = incAndWrap(counter, flows)
		end
		-- UDP checksums are optional, so using just IPv4 checksums would be sufficient here
		bufs:offloadUdpChecksums()
		queue:send(bufs)
		txCtr:update()
		--rxCtr:update()
	end
    --dumper(rxCtr, size, dumpfile)

	txCtr:finalize()
	--rxCtr:finalize()
end
