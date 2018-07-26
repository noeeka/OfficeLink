#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")
local general_template = [[
[general_template](!)
rtpstart=10000
rtpend=20000
]]

local general = [[
[general](general_template)
rtpstart=%s
rtpend=%s
]]

print(general_template)

local rtpstart = "10000"
local rtpend = "20000"

for row in db:nrows("SELECT * FROM configs WHERE config = 'sip';") do
    local ret, data = pcall(json.decode, row.items)
    if not ret then
        break
    end
    if nil ~= data.rtp_port_range then
        rtpstart = data.rtp_port_range[1]
        rtpend = data.rtp_port_range[2]
    end
end
print(string.format(general,
                       rtpstart,
                       rtpend
                   )
     )

db:close()

