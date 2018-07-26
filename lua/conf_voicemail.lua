#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")
local general_template = [[
[general_template](!)
format=wav49|gsm|wav
serveremail=asterisk
attach=yes
skipms=3000
silencethreshold=128
maxlogins=3
emaildateformat=%A, %B %d, %Y at %r
pagerdateformat=%A, %B %d, %Y at %r
sendvoicemail=yes
]]

local other_context = [[
[zonemessages]
eastern=America/New_York|'vm-received' Q 'digits/at' IMp
central=America/Chicago|'vm-received' Q 'digits/at' IMp
central24=America/Chicago|'vm-received' q 'digits/at' H N 'hours'
military=Zulu|'vm-received' q 'digits/at' H N 'hours' 'phonetic/z_p'
european=Europe/Copenhagen|'vm-received' a d b 'digits/at' HM
]]

local general = [[
[general](general_template)
maxmsg=%s
maxsecs=%s
minsecs=%s
saycid=%s
sayduration=%s
envelope=%s
review=%s
maxsilence=%s
]]

print(general_template)
print(other_context)

local maxsecs = "60"
local minsecs = "5"
local maxmsg = "20"
local greeting = 'no'

for row in db:nrows("SELECT * FROM configs WHERE config = 'voicemail';") do
    local ret, data = pcall(json.decode, row.items)
    if not ret then
        break
    end
    maxsecs = tonumber(data.maxsec)
    minsecs = tonumber(data.minsec)
    maxmsg = tonumber(data.maxmessage)
    if nil == maxsecs then
        maxsecs = '60';
    end
    if nil == minsecs then
        minsecs = '5'
    end
    if nil == maxmsg then
        maxmsg = '20'
    end
    if true == data.greeting or 'true' == data.greating then
        greeting = 'yes';
    end
end
local maxsilence = minsecs - 1
if maxsilence < 0 then
    maxsilence = 0
end
print(string.format(general,
                       maxmsg,
                       maxsecs,
                       minsecs,
                       greeting,
                       greeting,
                       greeting,
                       greeting,
                       3 --maxsilence
                   )
     )

db:close()

