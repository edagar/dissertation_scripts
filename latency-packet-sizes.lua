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

-- set addresses here
local DST_MAC		= "3C:FD:FE:05:AB:FF" -- resolved via ARP on GW_IP or DST_IP, can be overriden with a string here
local SRC_IP_BASE	= "10.10.1.0" -- actual address will be SRC_IP_BASE + random(0, flows)
local DST_IP		= "10.10.1.2"
local SRC_PORT		= 1234
local DST_PORT		= 319

local RUN_TIME = 15

-- answer ARP requests for this IP on the rx port
-- change this if benchmarking something like a NAT device
local RX_IP		= DST_IP
-- used to resolve DST_MAC
local GW_IP		= DST_IP
-- used as source IP to resolve GW_IP to DST_MAC
local ARP_IP	= SRC_IP_BASE

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
    rxDev:getTxQueue(0):setRate(0)

    local f = io.open("dump", "w")
    f:close()

    for _, size in ipairs({60, 128, 256, 512, 1024, 1500}) do
        print(("running #%d"):format(size))
        mg.startTask("loadSlave", txDev:getTxQueue(0), rxDev, size, args.flows)
        mg.startTask("timerSlave", txDev:getTxQueue(1), rxDev:getRxQueue(1), size, args.flows, size)
        mg.waitForTasks()
		if not mg.running() then
			break
        end
   end

    mg.waitForTasks()
end

local function fillUdpPacket(buf, len)
	buf:getUdpPacket():fill{
		ethSrc = "3C:FD:FE:05:CF:00",
		ethDst = "3C:FD:FE:05:9B:80",

		--ethSrc = "3C:FD:FE:05:94:C2",
		--ethDst = "3C:FD:FE:04:AB:02",

		ip4Src = SRC_IP,
		ip4Dst = DST_IP,
		udpSrc = SRC_PORT,
		udpDst = DST_PORT,
		pktLength = len
	}
end

_hist = hist:new()

function update_hist(val)
    _hist:update(val)
    --print("lat: " .. tostring(val) .. "\n")
end

function p_hist()
    _hist:print()
	_hist:save("histogram.csv")
end

function dumper(hist, size, filename)
    local f = io.open(filename, "a")
    f:write(("%d,%.2f,%.2f\n"):format(size, hist:avg(), hist:standardDeviation()))
    f:close()
    --print(("avg: %d"):format(hist:avg()))

end

function loadSlave(queue, rxDev, size, flows)
	local mempool = memory.createMemPool(function(buf)
		fillUdpPacket(buf, size)
	end)
	local bufs = mempool:bufArray()
	local counter = 0
	local txCtr = stats:newDevTxCounter(queue, "plain")
	local rxCtr = stats:newDevRxCounter(rxDev, "plain")

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
		rxCtr:update()
	end
	txCtr:finalize()
	rxCtr:finalize()
end

function timerSlave(txQueue, rxQueue, size, flows, n)
	if size < 84 then
		log:warn("Packet size %d is smaller than minimum timestamp size 84. Timestamped packets will be larger than load packets.", size)
		size = 84
	end
	local timestamper = ts:newUdpTimestamper(txQueue, rxQueue)
	mg.sleepMillis(1000) -- ensure that the load task is running
	local counter = 0
	local rateLimit = timer:new(0.001)
	local baseIP = parseIPAddress(SRC_IP_BASE)

	local runtime = timer:new(RUN_TIME-1)
	local hist = hist:new()

	while runtime:running() and mg.running() do
        local lat = timestamper:measureLatency(size, function(buf)
			fillUdpPacket(buf, size)
			local pkt = buf:getUdpPacket()
			pkt.ip4.src:set(baseIP + counter)
			counter = incAndWrap(counter, flows)
		end)

        if lat then
            hist:update(lat)
            --print(("lat: %d\n"):format(lat))
        end

		rateLimit:wait()
		rateLimit:reset()
	end

	--print the latency stats after all the other stuff
	--mg.sleepMillis(300)

    dumper(hist, n, "dump")
    hist:print()
    --hist:save(("hist_%d.csv"):format(n))
end
