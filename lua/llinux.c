#include <unistd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <string.h>
#include <error.h>
#include <errno.h>
#include <time.h>

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

static int linux_open(lua_State *L) {
  const char *path = luaL_checkstring(L, 1);
  int flags = luaL_checkinteger(L, 2);
  int fd = open(path, flags);
  lua_pushinteger(L, fd);
  return 1;
}

static int linux_close(lua_State *L) {
  int fd = luaL_checkinteger(L, 1);
  close(fd);
  return 1;
}

static int linux_write(lua_State *L) {
  int fd = luaL_checkinteger(L, 1);
  const char *buf = luaL_checkstring(L, 2);
  int len = luaL_checkinteger(L, 3);
  lua_pushinteger(L, write(fd, buf, len));
  return 1;
}

static int linux_read(lua_State *L) {
  int fd = luaL_checkinteger(L, 1);
  int len = luaL_checkinteger(L, 2);
  char buf[len];
  len = read(fd, buf, len);
  if(len > 0) {
    lua_pushlstring (L, buf, len);
  } else {
    lua_pushnil(L);
  }
  return 1;
}

static int linux_seek(lua_State *L) {
  int fd = luaL_checkinteger(L, 1);
  int offset = luaL_checkinteger(L, 2);
  int whence = luaL_checkinteger(L, 3);
  off_t ret = lseek(fd, offset, whence);
  lua_pushinteger(L, ret);
  return 1;
}

static int linux_time(lua_State *L) {
  struct timeval tv;
  struct timespec ts;
  if (clock_gettime(CLOCK_MONOTONIC, &ts) < 0) {
      gettimeofday(&tv, NULL);
      lua_pushnumber(L, tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0);
  } else {
      lua_pushnumber(L, ts.tv_sec * 1000.0 + (ts.tv_nsec / 1000000.0));
  }
  return 1;
}

static int linux_tcpserver(lua_State *L)
{
    int rc;
    struct addrinfo *ai_list;
    struct addrinfo *ai_ptr;
    struct addrinfo ai_hints;
    const char *node = luaL_checkstring(L, 1);
    const char *service = luaL_checkstring(L, 2);
    int nb_connection = luaL_checkinteger(L, 3);
    int new_s;

    memset(&ai_hints, 0, sizeof (ai_hints));
    /* If node is not NULL, than the AI_PASSIVE flag is ignored. */
    ai_hints.ai_flags |= AI_PASSIVE;
#ifdef AI_ADDRCONFIG
    ai_hints.ai_flags |= AI_ADDRCONFIG;
#endif
    ai_hints.ai_family = AF_UNSPEC;
    ai_hints.ai_socktype = SOCK_STREAM;
    ai_hints.ai_addr = NULL;
    ai_hints.ai_canonname = NULL;
    ai_hints.ai_next = NULL;

    ai_list = NULL;
    rc = getaddrinfo(node, service, &ai_hints, &ai_list);
    if (rc != 0) {
        perror("getaddrinfo");
        lua_pushnil(L);
        return 1;
    }

    new_s = -1;
    for (ai_ptr = ai_list; ai_ptr != NULL; ai_ptr = ai_ptr->ai_next) {
        int s;

        s = socket(ai_ptr->ai_family, ai_ptr->ai_socktype,
                   ai_ptr->ai_protocol);
        if (s < 0) {
            perror("socket");
            continue;
        } else {
            int enable = 1;
            rc = setsockopt(s, SOL_SOCKET, SO_REUSEADDR,
                            (void *)&enable, sizeof (enable));
            if (rc != 0) {
                close(s);
                perror("setsockopt");
                continue;
            }
        }

        rc = bind(s, ai_ptr->ai_addr, ai_ptr->ai_addrlen);
        if (rc != 0) {
            close(s);
            perror("bind");
            continue;
        }

        rc = listen(s, nb_connection);
        if (rc != 0) {
            close(s);
            perror("listen");
            continue;
        }

        new_s = s;
        break;
    }
    freeaddrinfo(ai_list);

    if (new_s < 0) {
        lua_pushnil(L);
        return 1;
    }
    lua_pushinteger(L, new_s);
    return 1;
}

static int linux_accept(lua_State *L)
{
    struct sockaddr_in addr;
    socklen_t addrlen;
    addrlen = sizeof(addr);
    int sfd = luaL_checkinteger(L, 1);
    int fd = accept(sfd, (struct sockaddr *)&addr, &addrlen);
    if(-1 == fd) {
      lua_pushnil(L);
      lua_pushnil(L);
      lua_pushnil(L);
    } else {
      lua_pushinteger(L, fd);
      lua_pushstring(L, inet_ntoa(addr.sin_addr));
      lua_pushinteger(L, addr.sin_port);
    }
    return 3;
}

static int _modbus_tcp_set_ipv4_options(int s)
{
    int rc;
    int option;

    /* Set the TCP no delay flag */
    /* SOL_TCP = IPPROTO_TCP */
    option = 1;
    rc = setsockopt(s, IPPROTO_TCP, TCP_NODELAY,
                    (const void *)&option, sizeof(int));
    if (rc == -1) {
        return -1;
    }

    /* If the OS does not offer SOCK_NONBLOCK, fall back to setting FIONBIO to
     * make sockets non-blocking */
    /* Do not care about the return value, this is optional */
#if !defined(SOCK_NONBLOCK) && defined(FIONBIO)
#ifdef OS_WIN32
    {
        /* Setting FIONBIO expects an unsigned long according to MSDN */
        u_long loption = 1;
        ioctlsocket(s, FIONBIO, &loption);
    }
#else
    option = 1;
    ioctl(s, FIONBIO, &option);
#endif
#endif

#ifndef OS_WIN32
    /**
     * Cygwin defines IPTOS_LOWDELAY but can't handle that flag so it's
     * necessary to workaround that problem.
     **/
    /* Set the IP low delay option */
    option = IPTOS_LOWDELAY;
    rc = setsockopt(s, IPPROTO_IP, IP_TOS,
                    (const void *)&option, sizeof(int));
    if (rc == -1) {
        return -1;
    }
#endif

    return 0;
}

static int _connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen,
                    const struct timeval *ro_tv)
{
    int rc = connect(sockfd, addr, addrlen);

#ifdef OS_WIN32
    int wsaError = 0;
    if (rc == -1) {
        wsaError = WSAGetLastError();
    }

    if (wsaError == WSAEWOULDBLOCK || wsaError == WSAEINPROGRESS) {
#else
    if (rc == -1 && errno == EINPROGRESS) {
#endif
        fd_set wset;
        int optval;
        socklen_t optlen = sizeof(optval);
        struct timeval tv = *ro_tv;

        /* Wait to be available in writing */
        FD_ZERO(&wset);
        FD_SET(sockfd, &wset);
        rc = select(sockfd + 1, NULL, &wset, NULL, &tv);
        if (rc <= 0) {
            /* Timeout or fail */
            return -1;
        }

        /* The connection is established if SO_ERROR and optval are set to 0 */
        rc = getsockopt(sockfd, SOL_SOCKET, SO_ERROR, (void *)&optval, &optlen);
        if (rc == 0 && optval == 0) {
            return 0;
        } else {
            errno = ECONNREFUSED;
            return -1;
        }
    }
    return rc;
}

/* Establishes a modbus TCP PI connection with a Modbus server. */
static int _modbus_tcp_pi_connect(lua_State *L)
{
    int rc;
    int s = -1;
    struct addrinfo *ai_list;
    struct addrinfo *ai_ptr;
    struct addrinfo ai_hints;
    const char *node = luaL_checkstring(L, 1);
    const char *service = luaL_checkstring(L, 2);
    int timeout = luaL_checkinteger(L, 3);
    const struct timeval tm = {timeout/1000, timeout*1000};
    memset(&ai_hints, 0, sizeof(ai_hints));
#ifdef AI_ADDRCONFIG
    ai_hints.ai_flags |= AI_ADDRCONFIG;
#endif
    ai_hints.ai_family = AF_UNSPEC;
    ai_hints.ai_socktype = SOCK_STREAM;
    ai_hints.ai_addr = NULL;
    ai_hints.ai_canonname = NULL;
    ai_hints.ai_next = NULL;

    ai_list = NULL;
    rc = getaddrinfo(node, service,
                     &ai_hints, &ai_list);
    if (rc != 0) {
        perror("getaddrinfo");
        lua_pushnil(L);
        return 1;
    }

    for (ai_ptr = ai_list; ai_ptr != NULL; ai_ptr = ai_ptr->ai_next) {
        int flags = ai_ptr->ai_socktype;

#ifdef SOCK_CLOEXEC
        flags |= SOCK_CLOEXEC;
#endif

#ifdef SOCK_NONBLOCK
        flags |= SOCK_NONBLOCK;
#endif

        s = socket(ai_ptr->ai_family, flags, ai_ptr->ai_protocol);
        if (s < 0)
            continue;

        if (ai_ptr->ai_family == AF_INET)
            _modbus_tcp_set_ipv4_options(s);

        rc = _connect(s, ai_ptr->ai_addr, ai_ptr->ai_addrlen, &tm);
        if (rc == -1) {
            close(s);
            s = -1;
            continue;
        }
        break;
    }

    freeaddrinfo(ai_list);

    if (s < 0) {
        lua_pushnil(L);
        return 1;
    }
    lua_pushinteger(L, s);
    return 1;
}

static int linux_recv(lua_State *L) {
  int fd = luaL_checkinteger(L, 1);
  int len = luaL_checkinteger(L, 2);
  int timeout = luaL_checkinteger(L, 3);
  struct timeval tv = {timeout/1000, timeout*1000};

  char buf[len];
  fd_set rset;

  /* Wait to be available in writing */
  FD_ZERO(&rset);
  FD_SET(fd, &rset);
  int rc = select(fd + 1, &rset, NULL, NULL, &tv);
  if (rc <= 0) {
    /* Timeout or fail */
    lua_pushnil(L);
    return 1;
  }
  len = recv(fd, buf, len, 0);
  if(len > 0) {
    lua_pushlstring (L, buf, len);
  } else {
    lua_pushnil(L);
  }
  return 1;
}

static const luaL_Reg linux_lib[] = {
  {"open",      linux_open},
  {"close",     linux_close},
  {"write",     linux_write},
  {"read",      linux_read},
  {"seek",      linux_seek},
  {"time",      linux_time},
  {"tcpserver", linux_tcpserver},
  {"tcpclient", _modbus_tcp_pi_connect},
  {"accept",    linux_accept},
  {"recv",      linux_recv},
  {NULL, NULL}
};

/* }====================================================== */



LUALIB_API int luaopen_llinux(lua_State *L) {
  luaL_register(L, "llinux", linux_lib);
#define SETCONST(EVENT) \
  lua_pushnumber(L, EVENT); \
  lua_setfield(L, -2, #EVENT)

  SETCONST(O_ACCMODE);
  SETCONST(O_RDONLY);
  SETCONST(O_WRONLY);
  SETCONST(O_RDWR);
  SETCONST(O_CREAT);
  SETCONST(O_EXCL);
  SETCONST(O_NOCTTY);
  SETCONST(O_TRUNC);
  SETCONST(O_APPEND);
  SETCONST(O_NONBLOCK);
  SETCONST(O_NDELAY);
  SETCONST(SEEK_SET);
  SETCONST(SEEK_CUR);
  SETCONST(SEEK_END);
  return 1;
}
