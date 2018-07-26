#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")
local general = [[
[general]
fullname = New User
userbase = 6000
hasvoicemail = yes
vmsecret = 1234
hassip = yes
hasiax = yes
hasmanager = no
callwaiting = yes
threewaycalling = yes
callwaitingcallerid = yes
transfer = yes
canpark = yes
cancallforward = yes
callreturn = yes
callgroup = 1
pickupgroup = 1
]]
print(general)

local user_template = [[
[user_template](!)
;fullname = 6001
registersip = no
host = dynamic
callgroup = 1
;mailbox = 6001
call-limit = 100
type = peer
;username = 6001
transfer = yes

callcounter = yes
context = DLPN_systec
;cid_number = 6001
;hasvoicemail = yes
;vmsecret = 6001
email = 
threewaycalling = no
hasdirectory = no
callwaiting = no
hasmanager = no
hasagent = no
hassip = yes
hasiax = no
;secret = 6001
nat = force_rport,comedia
canreinvite = no
dtmfmode = rfc2833
insecure = no
pickupgroup = 1

;macaddress = 6001
autoprov = yes
;label = 6001
linenumber = 1
LINEKEYS = 1
disallow = all
allow = ulaw,gsm
]]

local provider_template = [[
[provider_template](!)
;host = www.systec-pbx.net
;username = 80008
;secret = 80008
;trunkname = officelink_server
;context = DLPN_systec
nat = force_rport,comedia
hasexten = no
hasiax = no
hassip = yes
registeriax = no
registersip = yes
trunkstyle = voip
disallow = all
allow = all
keepalive = 10
insecure = invite
]]

print(user_template)
print(provider_template)

local sip_user = [[
[%s](user_template)
fullname = %s
mailbox = %s
username = %s
context = %s
cid_number = %s
hasvoicemail = %s
vmsecret = %s
email = %s
secret = %s
macaddress = %s
label = %s
allow = %s
]]

for row in db:nrows("SELECT * FROM sippeers;") do
    local hasvoicemail = "no"
    if string.len(row.voicemail_pin) > 0 then
        hasvoicemail = "yes"
    end
    if nil == row.email then
        row.email = ''
    end
    --local allow = 'ulaw,gsm'
    local allow = 'ulaw,alaw,gsm,ilbc,speex,g726,adpcm,lpc10,g729,g723'
    if '1' == row.video then
        --allow = 'ulaw,gsm,h264'
        allow = 'ulaw,alaw,gsm,ilbc,speex,g726,adpcm,lpc10,g729,g723,h263,h263p,h264'
    end
    print(string.format(sip_user,
                           row.extension, -- extension
                           row.nickname,  -- fullname
                           row.extension, -- mailbox
                           row.extension, -- username
                           --"DLPN_"..row.dialplan,  -- context
                           "DLPN_systec",  -- context
                           row.extension, -- cid_number
                           hasvoicemail,  -- hasvoicemail
                           row.voicemail_pin, -- vmsecret
                           row.email,         -- email
                           row.password,      -- secret
                           row.extension,     -- macaddress
                           row.extension,     -- label
                           allow            -- allow
                       )
         )
end

local sip_provider = [[
[%s](provider_template)
host = %s
username = %s
secret = %s
trunkname = %s
context = %s
]]

local tmp_address = ''
local tmp_user = ''

for row in db:nrows("SELECT * FROM providers;") do
    local name = row.name
    local user = row.user
    local password = row.password
    local is_repeat = false
    if password == nil then
        password = ''
    end
    if user == nil then
        user = ''
    end
    if 'pstn' == string.lower(row.type) then
        user = ''
        password = ''
    else
        if tmp_address == row.address and tmp_user == user then
           is_repeat = true 
        end
    end
    tmp_address = row.address
    tmp_user = user
    if not is_repeat then
        print(string.format(sip_provider,
                           name,     -- name
                           row.address,  -- host
                           user,     -- username
                           password, -- secret
                           row.name,     -- trunkname
                           -- "DLPN_"..row.dialplan  -- context
                           "DLPN_systec"  -- context
                       )
        )
   end
end

db:close()

