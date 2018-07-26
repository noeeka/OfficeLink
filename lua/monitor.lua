#! /usr/bin/env lua
local linux = require('llinux')
local epoll = require('lepoll')
local bit = require('bit')
local sqlite3 = require('lsqlite3')
local db = sqlite3.open("/var/log/asterisk/master.db")

R = {
    buf = "",
    timereduce = 60000,
    cdr_max = 600
}

function coroutine_sleep(timer)
    while linux.time() < timer and linux.time() + R.timereduce > timer do
        coroutine.yield()
    end
end

function cdr_clean()
    local cdr_count = 0
    for row in db:nrows("SELECT COUNT(*) FROM cdr;") do
        cdr_count = row['COUNT(*)']
    end
    if cdr_count >= R.cdr_max then
        local r_count = cdr_count - 500
        local sql = "delete from cdr where calldate <= (select calldate from cdr order by calldate asc limit " .. tostring(r_count) .. ",1);"
        db:exec(sql)
    end
end

idle_timer_handler = coroutine.wrap(function()
    local nginx_log_path = "/usr/local/nginx/logs/access.log"
    local asterisk_log_path = "/var/log/asterisk/messages"
    while true do
        local timer = linux.time() + 10000
        local nginx_log = io.open(nginx_log_path, "rb")
        if nginx_log then
            local nginx_log_len = nginx_log:seek('end')
            nginx_log:close()
            print("nginx_log_len", nginx_log_len)
            if nginx_log_len > 10000000 then
                os.execute("mv "..nginx_log_path.." "..nginx_log_path..".old")
                os.execute("kill -USR1 `cat /usr/local/nginx/logs/nginx.pid`")
            end
        end
        
        local asterisk_log = io.open(asterisk_log_path, "rb")
        if asterisk_log then
            local asterisk_log_len = asterisk_log:seek('end')
            asterisk_log:close()
            print("asterisk_log_len", asterisk_log_len)
            if asterisk_log_len > 10000000 then
                os.execute("mv "..asterisk_log_path.." "..asterisk_log_path..".old")
                os.execute('/usr/sbin/asterisk -x "logger reload"')
            end
        end
        cdr_clean()
        coroutine_sleep(timer)
    end
end)

function main()
    local stdin_fd = 0
    local io_handlers = {[stdin_fd]=stdin_handler}
    local efd = epoll.create(2)
    epoll.register(efd, stdin_fd, bit.bor(epoll.EPOLLIN, epoll.EPOLLET))
    while true do
        local events = epoll.wait(efd, 1000, 5)
        if nil == next(events) then
            idle_timer_handler()
        end
        for fd, event in pairs(events) do
            if bit.band(event, epoll.EPOLLIN) then
                if nil == io_handlers[fd] then
                else
                    R.buf = linux.read(fd, 1024)
                    io_handlers[fd]()
                end
            end
        end
    end
end

main()

