#! /usr/bin/env lua
local linux = require('llinux')
local epoll = require('lepoll')
local bit = require('bit')
local json = require("json")
local sqlite3 = require("lsqlite3")

R = {
    buf = "",
    key_down = false,
    key_timer = 0,
    tcpclients = {},
    action = nil,
    timereduce = 60000,
    log=function ( ... ) 
            print(os.date(), ...)
        end,
}

tcp_table = {
    GVER=function(fd, buf)
             local cmd = '1.1.0\r\n'
             linux.write(fd, cmd, string.len(cmd))
         end,
    RELOAD=function(fd, buf)
             local cmd = 'RELOAD OK\r\n'
             linux.write(fd, cmd, string.len(cmd))
             R.action = 'reload'
          end
}

stdin_handler = coroutine.wrap(function(fd)
    local buf = ""
    local match = false
    while true do
        while 1 == string.len(R.buf) do
            coroutine.yield()
        end
        buf = buf..R.buf
        match = false
        for x in string.gmatch(buf, "(.*)\n") do
            match = true
        end
        if match then
            buf = ""
        end
        coroutine.yield()
    end
end)

key_handler = coroutine.wrap(function(fd)
    while true do
        R.log('key down', R.buf)
        if '0\n' == R.buf then
            R.key_down = true
            R.key_timer = linux.time() + 5000
        else
            R.key_down = false
        end
        coroutine.yield()
    end
end)

function coroutine_sleep(timer)
    while linux.time() < timer and linux.time() + R.timereduce > timer do
        coroutine.yield()
    end
end

idle_timer_handler = coroutine.wrap(function()
    local dir = 0
    local dutys = {1, 2, 3 , 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 98, 100, 98, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5, 4, 3, 2, 1}
    local led_file = io.open('/sys/class/pwm/ehrpwm.2:0/duty_percent', 'w')
    --local run_led_file = io.open('/sys/class/gpio/gpio65/value', 'w')
    while true do
        --local rc = run_led_file:write('0')
        --run_led_file:flush()
        local timer = linux.time()
        for id, duty in pairs(dutys) do
            if nil ~= R.action then
                break
            end
            local rc = led_file:write(''..duty)
            led_file:flush()
            timer = linux.time() + 100
            coroutine_sleep(timer)
        end
        if R.key_down and R.key_timer < linux.time() and R.key_timer + R.timereduce > linux.time() then
            R.key_down = false
            R.log('long press')
            for i=1,21,1 do
                timer = linux.time() + 100
                led_file:write(''..((i%2)*100))
                led_file:flush()
                coroutine_sleep(timer)
            end
            os.execute('rm -rf /var/lib/asterisk/moh/*')
            os.execute('rm -rf /var/www/html/avatar/*')
            os.execute('rm -rf /var/log/asterisk/voicemail/default/*')
            os.execute('sqlite3 /var/lib/asterisk/realtime.sqlite3 < /usr/share/restore.sql')
            os.execute('sqlite3 /var/log/asterisk/master.db < /usr/share/records_restore.sql')
            os.execute('cp /usr/share/interfaces.restore /etc/network/interfaces')
            os.execute('ln -sf /usr/share/zoneinfo/Etc/GMT+8 /etc/localtime')
            os.execute('date > /home/restore.lua.record')
            os.execute('sync;sync;sync;sync;sync;sync')
            os.execute('asterisk -rx reload')
            os.execute('/etc/init.d/network restart')
        end
        if 'reload' == R.action then
            for i=1,21,1 do
                timer = linux.time() + 100
                led_file:write(''..((i%2)*100))
                led_file:flush()
                coroutine_sleep(timer)
            end
            R.action = nil
        elseif nil == R.action then
            timer = linux.time() + 700
            while linux.time() < timer and linux.time() + R.timereduce > timer and nil == R.action do
                coroutine.yield()
            end
        end
        --local rc = run_led_file:write('1')
        --run_led_file:flush()
    end
end)

function tcp_in_handler(fd)
    local match = false
    if R.tcpclients[fd].timer < linux.time() or R.tcpclients[fd].timer > linux.time() + R.timereduce or string.len(R.tcpclients[fd].buf) > 1024 then
        R.tcpclients[fd].buf = ''
    end
    R.tcpclients[fd].timer = linux.time() + 500
    R.tcpclients[fd].buf = R.tcpclients[fd].buf .. R.buf
    buf = R.tcpclients[fd].buf
    for x, y in string.gmatch(buf, "(%w+)(.*)\r\n") do
        if "function" == type(tcp_table[x]) then
            R.log("tcp-rcv", fd, x, y)
            tcp_table[x](fd, y)
        end 
        match = true
    end 
    if match then
        R.tcpclients[fd].buf = ''
    end
end 

function main()
    os.execute('echo -n 1 > /dev/led-work')

    os.execute('echo 65 > /sys/class/gpio/export')
    os.execute('echo out > /sys/class/gpio/gpio65/direction')
    os.execute('echo 1 > /sys/class/gpio/gpio65/value')
    
    os.execute('echo 1 >  /sys/class/pwm/ehrpwm.2:0/request')
    os.execute('echo 100 > /sys/class/pwm/ehrpwm.2:0/period_freq')
    os.execute('echo 1 > /sys/class/pwm/ehrpwm.2:0/duty_percent')
    os.execute('echo 1 > /sys/class/pwm/ehrpwm.2:0/run')
    
    os.execute('echo 44 > /sys/class/gpio/export')
    os.execute('echo in > /sys/class/gpio/gpio44/direction')
    --os.execute('echo falling > /sys/class/gpio/gpio44/edge')
    os.execute('echo both > /sys/class/gpio/gpio44/edge')
    
    local stdin_fd = 0
    local key_fd = linux.open('/sys/class/gpio/gpio44/value', linux.O_RDONLY)
    local sfd = linux.tcpserver("0.0.0.0", "10086", 5)
    local io_handlers = {[stdin_fd]=stdin_handler, [key_fd]=key_handler}
    local efd = epoll.create(2)
    epoll.register(efd, stdin_fd, bit.bor(epoll.EPOLLIN, epoll.EPOLLET))
    epoll.register(efd, key_fd, bit.bor(epoll.EPOLLIN, epoll.EPOLLET))
    epoll.register(efd, sfd, bit.bor(epoll.EPOLLIN, epoll.EPOLLET))
    while true do
        local events = epoll.wait(efd, 50, 5)
        if nil == next(events) then
            idle_timer_handler()
        end
        for fd, event in pairs(events) do
            if bit.band(event, epoll.EPOLLIN) then
                if sfd == fd then
                    local cfd, caddr, cport = linux.accept(sfd)
                    epoll.register(efd, cfd, bit.bor(epoll.EPOLLIN, epoll.EPOLLET))
                    io_handlers[cfd] = tcp_in_handler
                    R.tcpclients[cfd] = {addr=caddr .. ":" .. cport, timer=linux.time(), buf=''}
                    R.log("conn", R.tcpclients[cfd].addr)
                else
                    if fd == key_fd then
                        linux.seek(fd, linux.SEEK_SET, 0)
                    end
                    R.buf = linux.read(fd, 1024)
                    if nil == R.buf then
                        if fd ~= key_fd and fd ~= stdin_fd then
                            epoll.unregister(efd, fd)
                            io_handlers[fd] = nil
                            R.log("disc", R.tcpclients[fd].addr)
                            R.tcpclients[fd] = nil
                            linux.close(fd)
                        end
                    elseif nil ~= io_handlers[fd] then
                        io_handlers[fd](fd)
                    end
                end
            end
        end
    end
end

main()

