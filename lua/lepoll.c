#include <unistd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <error.h>
#include <errno.h>
#include <string.h>

#include "lua.h"
#include "lauxlib.h"

#if LUA_VERSION_NUM > 501
/*
** Lua 5.2
*/
#define lua_strlen lua_rawlen
/* luaL_typerror always used with arg at ndx == NULL */
#define luaL_typerror(L,ndx,str) luaL_error(L,"bad argument %d (%s expected, got nil)",ndx,str)
/* luaL_register used once, so below expansion is OK for this case */
#define luaL_register(L,name,reg) lua_newtable(L);luaL_setfuncs(L,reg,0)
/* luaL_openlib always used with name == NULL */
#define luaL_openlib(L,name,reg,nup) luaL_setfuncs(L,reg,nup)

#if LUA_VERSION_NUM > 502
/*
** Lua 5.3
*/
#define luaL_checkint(L,n)  ((int)luaL_checkinteger(L, (n)))
#endif
#endif

#define DSERR() \
    lua_pushnil(L); \
    lua_pushstring(L, strerror(errno)); \
    return 2

typedef enum EPOLL_EVENTS EVENTMASK;

static int ep_create(lua_State *L){
    int epfd;
    int size = luaL_checkinteger(L, 1);
    if((epfd = epoll_create(size)) == -1){
        DSERR();
    }
    lua_pushinteger(L, epfd);
    return 1;
}

static int ep_event_add(lua_State *L){
    int epfd,fd;
    EVENTMASK eventmask;
    epfd = luaL_checkinteger(L, 1);
    fd = luaL_checkinteger(L, 2);
    eventmask = luaL_checkinteger(L, 3);

    struct epoll_event ev;
    ev.data.fd = fd;
    ev.events = eventmask;

    if(epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev) == -1){
        DSERR();
    }
    lua_pushboolean(L, 1);
    return 1;
}

static int ep_event_mod(lua_State *L){
    int epfd, fd;
    EVENTMASK eventmask;
    
    epfd = luaL_checkinteger(L, 1);
    fd = luaL_checkinteger(L,2);
    eventmask = luaL_checkinteger(L,3);

    struct epoll_event ev;
    ev.data.fd = fd;
    ev.events = eventmask;

    if(epoll_ctl(epfd, EPOLL_CTL_MOD, fd, &ev) == -1){
        DSERR();
    }
    lua_pushboolean(L, 1);
    return 1;
}

static int ep_event_del(lua_State *L){
    int epfd, fd;

    epfd = luaL_checkinteger(L, 1);
    fd = luaL_checkinteger(L, 2);

    if(epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL) == -1){
        DSERR();
    }
    lua_pushboolean(L, 1);
    return 1;
}

static int ep_wait(lua_State *L){
    int i, n, epfd, timeout, max_events;

    epfd = luaL_checkinteger(L, 1);
    timeout = luaL_checkinteger(L, 2);
    max_events = luaL_checkinteger(L, 3);

    struct epoll_event events[max_events];

    if((n = epoll_wait(epfd, events, max_events, timeout)) == -1){
        DSERR();
    }
    lua_newtable(L);
    for(i=0; i<n; ++i){
        lua_pushinteger(L, events[i].data.fd);
        lua_pushinteger(L, events[i].events);
        lua_settable(L, -3);
    }
    return 1;
}

static int ep_close(lua_State *L){
    int fd;
    fd = luaL_checkinteger(L, 1);
    if(close(fd) == -1){
        DSERR();
    }
    lua_pushboolean(L, 1);
    return 1;
}

static const luaL_Reg epoll_lib[] = {
  {"create"      , ep_create},
  {"register"    , ep_event_add},
  {"modify"      , ep_event_mod},
  {"unregister"  , ep_event_del},
  {"wait"        , ep_wait},
  {"close"       , ep_close},
  {NULL, NULL}
};

LUALIB_API int luaopen_lepoll(lua_State *L) {
  luaL_register(L, "lepoll", epoll_lib);
#define SETCONST(EVENT) \
  lua_pushnumber(L, EVENT); \
  lua_setfield(L, -2, #EVENT)

  SETCONST(EPOLLIN);
  SETCONST(EPOLLPRI);
  SETCONST(EPOLLOUT);
  SETCONST(EPOLLRDNORM);
  SETCONST(EPOLLRDBAND);
  SETCONST(EPOLLWRNORM);
  SETCONST(EPOLLWRBAND);
  SETCONST(EPOLLMSG);
  SETCONST(EPOLLERR);
  SETCONST(EPOLLHUP);
  SETCONST(EPOLLRDHUP);
  SETCONST(EPOLLONESHOT);
  SETCONST(EPOLLET);
  return 1;
}
