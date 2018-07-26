#!/usr/bin/env lua
local json = require("json")
local sqlite3 = require("lsqlite3")
local db = sqlite3.open("/var/lib/asterisk/realtime.sqlite3")

local general = [[
[general]
]]

local default = [[
[default]
parkext => %s
parkpos => %s
context => parkedcalls
parkingtime => %s
]]

local conf = {digit_timeout=1000, parking_res={extension=700, space={700, 720}, timeout=20}, blind='#1', hungup='*0', transfer='*2', parking='#72', app_map={{name='office', digit='*8', channel='self', application='Dial', args={'SIP/6002'}}}}

local data

for row in db:nrows("SELECT * FROM configs WHERE config = 'callfeature';") do
    data = json.decode(row.items)
    break
end

if 'table' == type(data) then 
    if nil ~= data.digit_timeout then conf.digit_timeout = data.digit_timeout end
    if nil ~= data.blind then conf.blind = data.blind end
    if nil ~= data.hungup then conf.hungup = data.hungup end
    if nil ~= data.transfer then conf.transfer = data.transfer end
    if nil ~= data.parking then conf.parking = data.parking end
    if 'table' == type(data.parking_res) then
        if nil ~= data.parking_res.extension then conf.parking_res.extension = data.parking_res.extension end
        if nil ~= data.parking_res.timeout then conf.parking_res.timeout = data.parking_res.timeout end
        if 'table' == type(data.parking_res.space) then conf.parking_res.space = data.parking_res.space end
    end
end

print(general)

print(string.format(default,
        conf.parking_res.extension,
        table.concat(conf.parking_res.space, '-'),
        conf.parking_res.timeout
    )
)

db:close()

