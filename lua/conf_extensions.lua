#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")

local days_map = {'mon','tue','wed','thu','fri','sat','sun'}
local context = [[
[%s]
]]

local extension = 'exten => %s, %s, %s(%s)\n'
local extension_noargs = 'exten => %s, %s, %s()\n'

local systecrule = string.format(context, 'systecrule')

local systemrule = string.format(context, 'systemrule')
systemrule = systemrule .. string.format(extension, 's', '1', 'GotoIf', '$[${SIP_HEADER(X-OfficeLink)}NULL!=NULL]?DLPN_systec,${SIP_HEADER(X-OfficeLink)},1:voicemenu')
systemrule = systemrule .. string.format(extension, 's', 'n(voicemenu)', 'NoOp', 'OfficeLink')
systemrule = systemrule .. string.format(extension, 's', 'n', 'Background', '/var/lib/asterisk/moh/manolo_camp-morning_coffee')
systemrule = systemrule .. string.format(extension, 's', 'n', 'WaitExten', '5')
systemrule = systemrule .. 'include => systecrule\n'

local voicemail_exten = '10000'
local dial_voicemail = false

for row in db:nrows("SELECT * FROM configs WHERE config = 'voicemail';") do
    local ret, data = pcall(json.decode, row.items)
    if not ret then
        break
    end
    voicemail_exten = data.extension
    if true == data.dial_voicemail or 'true' == data.dial_voicemail then
        dial_voicemail = true
    end
end

if nil == voicemail_exten then
    voicemail_exten = '10000'
end
systemrule = systemrule .. string.format(extension, voicemail_exten, 1, 'VoiceMailMain', '${CALLERID(num)}@default')
systemrule = systemrule .. string.format(extension_noargs, voicemail_exten, 'n', 'Hangup')

for row in db:nrows("SELECT * FROM sippeers;") do
    local ret, days = pcall(json.decode, row.transfer_days)
    if not ret then
        days = {}
    end
    local ret, times = pcall(json.decode, row.transfer_time)
    if not ret then
        times = {}
    end
    local days_t = {}
    for k, v in pairs(days) do
        local vv = tonumber(v)
        if nil ~= days_map[vv] then
            table.insert(days_t, days_map[vv])
        end
    end
    local times_str = '*'
    local days_str = '*'
    local transfer_target = row.transfer_target
    if nil == transfer_target or '' == transfer_target then
        transfer_target = row.extension
    end
    if next(times) then
        times_str = table.concat(times, '-')
    end
    if next(days_t) then
        days_str = table.concat(days_t, '&')
    end
    if not string.match(times_str, '%d?%d:%d?%d%-%d?%d:%d?%d') then
        times_str = '*'
    end

    times_days = times_str .. ',' .. days_str
    systecrule = systecrule .. string.format(extension, row.extension, '1', 'NoOp', 'systecrule')
    ring_timeout = tonumber(row.ring_timeout)
    if ring_timeout > 0 then
    else
        ring_timeout = ''
    end
    if 'direct' ~= row.transfer_style then
        systecrule = systecrule .. string.format(extension, row.extension, 'n', 'Dial', 'SIP/${EXTEN},'..ring_timeout..',tTkK')
    end
    if 'absent' == row.transfer_style then
        systecrule = systecrule .. string.format(extension, row.extension, 'n', 'GotoIf', '$[${DIALSTATUS}=BUSY|${DIALSTATUS}=NOANSWER|${DIALSTATUS}=CHANUNAVAIL]?checktime:hangup')
    elseif 'busy' == row.transfer_style then
        systecrule = systecrule .. string.format(extension, row.extension, 'n', 'GotoIf', '$[${DIALSTATUS}=BUSY|${DIALSTATUS}=NOANSWER|${DIALSTATUS}=CHANUNAVAIL]?checktime:hangup')
    else
        systecrule = systecrule .. string.format(extension, row.extension, 'n', 'Goto', '${EXTEN},checktime')
    end
    
    if next(days_t) then
        systecrule = systecrule .. string.format(extension, row.extension, 'n(checktime)', 'GotoIfTime', times_days..',*,*,?transfer:hangup')
    else
        systecrule = systecrule .. string.format(extension, row.extension, 'n(checktime)', 'GotoIf', '1=1?hangup:hangup')
    end
    if 'dial' == row.transfer_type then
        systecrule = systecrule .. string.format(extension, row.extension, 'n(transfer)', 'Dial', 'SIP/'..transfer_target..','..ring_timeout..',tTkK')
    elseif 'voicemail' == row.transfer_type then
        systecrule = systecrule .. string.format(extension, row.extension, 'n(transfer)', 'VoiceMail', transfer_target..'@default')
    end
    systecrule = systecrule .. string.format(extension_noargs, row.extension, 'n(hangup)', 'Hangup')
    if dial_voicemail then
        systecrule = systecrule .. string.format(extension, '#'..row.extension, '1', 'VoiceMail', row.extension..'@default')
        systecrule = systecrule .. string.format(extension_noargs, '#'..row.extension, 'n(hangup)', 'Hangup')
    end
end

for row in db:nrows("SELECT * FROM ringgroups;") do
    local ret, members = pcall(json.decode, row.members)
    local timeout = row.timeout
    if tonumber(timeout) <= 0 then
        timeout = ''
    end
    if not ret then
    elseif 'table' == type(members) and next(members) then
        systecrule = systecrule .. string.format(extension, row.extension, 1, 'Dial', 'SIP/'..table.concat(members, '&SIP/')..',' ..timeout)
        systecrule = systecrule .. string.format(extension_noargs, row.extension, 'n(hangup)', 'Hangup')
    end
end

for row in db:nrows("SELECT * FROM meetme;") do
    systecrule = systecrule .. string.format(extension, row.confno, 1, 'MeetMe', '${EXTEN},MsI')
    systecrule = systecrule .. string.format(extension_noargs, row.confno, 'n(hangup)', 'Hangup')
end

local ivrs = ''
local default_music = '/var/lib/asterisk/moh-default/manolo_camp-morning_coffee'

for row in db:nrows("SELECT * FROM ivrs;") do
    local rc = string.format(context, 'voicemenu_' .. row.name)
    rc = rc .. string.format(extension, row.extension, '1', 'NoOp', row.name)
    --rc = rc .. string.format(extension_noargs, row.extension, 'n', 'Progress')
    if 'Default' == row.music then
        rc = rc .. string.format(extension, row.extension, 'n', 'Background', default_music)
    else
        rc = rc .. string.format(extension, row.extension, 'n', 'Background', '/var/lib/asterisk/moh/'..row.music..'/'..row.music)
    end
    rc = rc .. string.format(extension, row.extension, 'n', 'WaitExten', row.timeout)
    --rc = rc .. string.format(extension, row.extension, 'n', 'WaitExten', row.timeout..',m('..row.music..')')
    rc = rc .. 'include => systecrule\n'
    print(rc)
    systecrule = systecrule .. string.format(extension, row.extension, 1, 'Goto', 'voicemenu_' .. row.name .. ','..row.extension..',1')
end

print(systecrule)

for row in db:nrows("SELECT * FROM outrouters;") do
    local rule = '_' .. row.rule .. '.'
    local target = 'SIP/' .. row.provider .. '/' .. row.append .. '${EXTEN:' .. row.filter .. '}'
    systemrule = systemrule .. string.format(extension, rule, 1, 'Dial', target)
    systemrule = systemrule .. string.format(extension_noargs, rule, 'n', 'Hangup')
end

print(systemrule)

local include = 'include %s\n'

local rc = string.format(context, 'DLPN_systec')
rc = rc .. 'include => systecrule\n'
rc = rc .. 'include => systemrule\n'
rc = rc .. 'include => parkedcalls\n'
print(rc)

db:close()

