#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")
local general_template = [[
[general_template](!)
context = public  
allowoverlap = no  
udpbindaddr = 0.0.0.0  
tcpenable = no  
tcpbindaddr = 0.0.0.0  
transport = udp  
srvlookup = yes  
language = cn  
auth_options_requests = yes  
outofcall_message_context = messages  
subscribecontext = default
allowexternaldomains = yes
allowguest = yes
allowsubscribe = yes
allowtransfer = yes
alwaysauthreject = no
autodomain = no
callevents = no
checkmwi = 10
compactheaders = no
defaultexpiry = 120
dumphistory = no
externrefresh = 10
g726nonstandard = no
jbenable = no
jbforce = no
jblog = no
maxcallbitrate = 384
maxexpiry = 3600
minexpiry = 60
mohinterpret = default
notifyringing = yes
pedantic = no
progressinband = yes
promiscredir = no
realm = OfficeLink
recordhistory = no
registerattempts = 0
registertimeout = 20
relaxdtmf = no
sendrpid = no
sipdebug = no
t1min = 100
t38pt_udptl = no
tos_audio = none
tos_sip = none
tos_video = none
trustrpid = no
useragent = OfficeLink
usereqphone = no
videosupport = yes
disallow = all
allow = ulaw,alaw,gsm,h264
rtptimeout=60                  
rtpholdtimeout=300             
mwi_from = OfficeLink     
sdpsession = OfficeLink   
vmexten = OfficeLink
match_auth_username=yes
]]

local other_context = [[
[basic-options](!)
dtmfmode = rfc2833
context = from-office
type = friend
[natted-phone](!,basic-options)
directmedia = no
host = dynamic
[public-phone](!,basic-options)
directmedia = yes
[my-codecs](!)
disallow = all
allow = ilbc
allow = g729
allow = gsm
allow = g723
allow = ulaw
[ulaw-phone](!)
disallow = all
allow = ulaw
]]

local general = [[
[general](general_template)
udpbindaddr = 0.0.0.0%s
language = %s
]]

print(general_template)
print(other_context)

local port = ""

for row in db:nrows("SELECT * FROM configs WHERE config = 'sip';") do
    local ret, data = pcall(json.decode, row.items)
    if not ret then
        break
    end
    if nil ~= data.sip_port then
        port = ":" .. data.sip_port
    end
end

local language = 'cn'

for row in db:nrows("SELECT * FROM configs WHERE config = 'language';") do
    local ret, data = pcall(json.decode, row.items)
    if not ret then
        break
    end
    if nil ~= data.language then
        language = data.language
    end
end

print(string.format(general,
                       port,
                       language
                   )
     )

db:close()

