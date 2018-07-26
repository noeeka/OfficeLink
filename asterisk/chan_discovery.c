#include "asterisk.h"

ASTERISK_FILE_VERSION(__FILE__, "$Revision$")

#include <signal.h>
#include <sys/signal.h>
#include <regex.h>
#include <inttypes.h>

#include "asterisk/network.h"
#include "asterisk/paths.h"	/* need ast_config_AST_SYSTEM_NAME */
#include "asterisk/lock.h"
#include "asterisk/config.h"
#include "asterisk/module.h"
#include "asterisk/pbx.h"
#include "asterisk/sched.h"
#include "asterisk/io.h"
#include "asterisk/rtp_engine.h"
#include "asterisk/udptl.h"
#include "asterisk/acl.h"
#include "asterisk/manager.h"
#include "asterisk/callerid.h"
#include "asterisk/cli.h"
#include "asterisk/musiconhold.h"
#include "asterisk/dsp.h"
#include "asterisk/pickup.h"
#include "asterisk/parking.h"
#include "asterisk/srv.h"
#include "asterisk/astdb.h"
#include "asterisk/causes.h"
#include "asterisk/utils.h"
#include "asterisk/file.h"
#include "asterisk/astobj2.h"
#include "asterisk/dnsmgr.h"
#include "asterisk/devicestate.h"
#include "asterisk/netsock2.h"
#include "asterisk/localtime.h"
#include "asterisk/abstract_jb.h"
#include "asterisk/threadstorage.h"
#include "asterisk/translate.h"
#include "asterisk/ast_version.h"
#include "asterisk/data.h"
#include "asterisk/aoc.h"
#include "asterisk/message.h"
#include "sip/include/sip.h"
#include "sip/include/globals.h"
#include "sip/include/config_parser.h"
#include "sip/include/reqresp_parser.h"
#include "sip/include/sip_utils.h"
#include "asterisk/sdp_srtp.h"
#include "asterisk/ccss.h"
#include "asterisk/xml.h"
#include "sip/include/dialog.h"
#include "sip/include/dialplan_functions.h"
#include "sip/include/security_events.h"
#include "sip/include/route.h"
#include "asterisk/sip_api.h"
#include "asterisk/app.h"
#include "asterisk/bridge.h"
#include "asterisk/stasis.h"
#include "asterisk/stasis_endpoints.h"
#include "asterisk/stasis_system.h"
#include "asterisk/stasis_channels.h"
#include "asterisk/features_config.h"
#include "asterisk/http_websocket.h"
#include "asterisk/format_cache.h"

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <bits/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <error.h>
#include <errno.h>
#include <time.h>
#include <sys/epoll.h>

#define MAX_EP_EVT_NUM       5
#define MAX_EP_FD_NUM        10
#define MAX_BUF_SIZE         1024
#define EPOLL_TIME_OUT       1000

static int ssdpefd  = -1;
static int ssdpsock  = -1;
static int ssdp_reloading = FALSE;
static enum channelreloadreason ssdp_reloadreason;

static pthread_t monitor_thread = AST_PTHREADT_NULL;
AST_MUTEX_DEFINE_STATIC(monlock);
AST_MUTEX_DEFINE_STATIC(ssdp_reload_lock);
static int unload_module(void);

static int udp_s_addr(struct sockaddr_in *addr, int port) {
    bzero(addr,sizeof(struct sockaddr_in));
    addr->sin_family = AF_INET;
    addr->sin_addr.s_addr = htonl(INADDR_ANY);
    addr->sin_port = htons(port);
    return 0;
}
#if 0
static int udp_c_addr(struct sockaddr_in *addr, const char *ip, int port) {
    bzero(addr,sizeof(struct sockaddr_in));
    addr->sin_family = AF_INET;
    addr->sin_addr.s_addr = inet_addr(ip);
    addr->sin_port = htons(port);
    return 0;
}
#endif

static int udp_socket(struct sockaddr_in *addr, const char *mip) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    unsigned char is_broadcast = 0;
    if(-1 == fd) {
		ast_log(LOG_ERROR, "-1 == socket\n");
        return -1;
    }
    int opt = 0;
    if(0 == strcmp("255.255.255.255", mip)) {
        opt = 1;
        is_broadcast = 1;
    }
    if(setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(int)) != 0) {
      perror("setsockopt SOL_SOCKET != 0");
      return -1;
    }
    if(NULL != mip && !is_broadcast) {
        struct ip_mreq mreq;
        mreq.imr_multiaddr.s_addr = inet_addr(mip);
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);

        if(setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(struct ip_mreq)) != 0) {
		    ast_log(LOG_ERROR, "setsockopt IPPROTO_IP != 0\n");
            return -1;
        }
    }

    opt = 1;
    if(setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(int)) != 0) {
		ast_log(LOG_ERROR, "setsockopt SO_REUSEADDR != 0\n");
        return -1;
    }

    if(0 != addr->sin_port) {
        if(bind(fd ,(struct sockaddr *)addr, sizeof(struct sockaddr)) == -1) {
		    ast_log(LOG_ERROR, "-1 == bind\n");
            return -1;
        }
    }

    return fd;
}

static int epoll_add(int efd, int fd) {
    struct epoll_event ev;
    ev.data.fd = fd;
    ev.events = EPOLLIN|EPOLLET;
    if(0 != epoll_ctl(efd, EPOLL_CTL_ADD, fd, &ev)) {
        return -1;
    }
    return 0;
}

static int ssdp_load(void) {
    struct sockaddr_in addr;
    char ip[16] = "255.255.255.255";
    int port = 10086;
    struct ast_config *cfg;
    struct ast_variable *v;
    struct ast_flags config_flags = { 0 };
    char *config_file = "sip.conf";

    if (!(cfg = ast_config_load(config_file, config_flags))) {
        ast_log(LOG_NOTICE, "Unable to open configuration file %s!\n", config_file);
        return -1;
    } else if (cfg == CONFIG_STATUS_FILEINVALID) {
        ast_log(LOG_NOTICE, "Config file %s has an invalid format\n", config_file);
        return -1;
    }

    for (v = ast_variable_browse(cfg, "general"); v; v = v->next) {
        if(!strcmp(v->name, "ssdp_ip")) {
            strncpy(ip, v->value, sizeof(ip)-1);
        } else if(!strcmp(v->name, "ssdp_port")) {
            port = atoi(v->value);
        }
    }
 
    ast_config_destroy(cfg);
    
    ast_verb(1, "ip %s port %d\n", ip, port);
    udp_s_addr(&addr, port);
    ssdpsock = udp_socket(&addr, ip);

    if(-1 == ssdpsock) {
		ast_log(LOG_ERROR, "-1 == udp_socket\n");
        return -1;
    }
    ast_verb(1, "ssdpsock %d\n", ssdpsock);

    ssdpefd = epoll_create(MAX_EP_FD_NUM);
    if(ssdpefd < 0) {
        close(ssdpsock);
		ast_log(LOG_ERROR, "epoll_create < 0\n");
        return -1;
    }
    ast_verb(1, "ssdpefd %d\n", ssdpefd);

    if(-1 == epoll_add(ssdpefd, ssdpsock)) {
        close(ssdpsock);
        close(ssdpefd);
		ast_log(LOG_ERROR, "-1 == epoll_add\n");
        return -1;
    }
    return 0;
}

static void *do_monitor(void *data)
{   
    struct sockaddr_in c_addr;
    char buf[MAX_BUF_SIZE];

    socklen_t iplen =  sizeof(struct sockaddr);
    struct epoll_event events[MAX_EP_EVT_NUM];
    int i, len;
	int reloading;
    ssdp_load();
	/* From here on out, we die whenever asked */
	for(;;) {
		/* Check for a reload request */
		ast_mutex_lock(&ssdp_reload_lock);
		reloading = ssdp_reloading;
		ssdp_reloading = FALSE;
		ast_mutex_unlock(&ssdp_reload_lock);
		if (reloading) {
			ast_verb(1, "Reloading SSDP\n");
            if(ssdpsock > -1) {close(ssdpsock);}
            if(ssdpefd > -1) {close(ssdpefd);}
            ssdp_load();
		}
        int nfds = epoll_wait(ssdpefd, events, MAX_EP_EVT_NUM, EPOLL_TIME_OUT);
        if(0 == nfds) {
			ast_verb(1, "epoll timeout\n");
            continue;
        }
        for(i=0; i < nfds; ++i) {
            if(events[i].events & EPOLLIN) {
                len = recvfrom(events[i].data.fd, buf, MAX_BUF_SIZE, 0, (struct sockaddr *)&c_addr, &iplen);
                if(len > 0) {
                    buf[len] = '\0';
                    ast_verb(1, "len %d %s\n", len, buf);
                    len = sendto(events[i].data.fd, buf, len, 0, &c_addr, iplen);
                    ast_verb(1, "send len %d\n", len);
                } else {
                    ast_verb(1, "len %d", len);
                }
            } else {
                ast_log(LOG_ERROR, "events not support %d", events[i].events);
            }
        }
	}
	/* Never reached */
	return NULL;
}

/*! \brief Start the channel monitor thread */
static int restart_monitor(void)
{
	/* If we're supposed to be stopped -- stay stopped */
	if (monitor_thread == AST_PTHREADT_STOP)
		return 0;
	ast_mutex_lock(&monlock);
	if (monitor_thread == pthread_self()) {
		ast_mutex_unlock(&monlock);
		ast_log(LOG_WARNING, "Cannot kill myself\n");
		return -1;
	}
	if (monitor_thread != AST_PTHREADT_NULL && monitor_thread != AST_PTHREADT_STOP) {
		/* Wake up the thread */
		pthread_kill(monitor_thread, SIGURG);
	} else {
		/* Start a new monitor */
		if (ast_pthread_create_background(&monitor_thread, NULL, do_monitor, NULL) < 0) {
			ast_mutex_unlock(&monlock);
			ast_log(LOG_ERROR, "Unable to start monitor thread.\n");
			return -1;
		}
	}
	ast_mutex_unlock(&monlock);
	return 0;
}

static int load_module(void)
{
	ast_verbose("SSDP channel loading...\n");
    restart_monitor();
	return AST_MODULE_LOAD_SUCCESS;
}

static int unload_module(void)
{
	ast_verbose("SSDP channel unloading...\n");
    ast_mutex_lock(&monlock);
	if (monitor_thread && (monitor_thread != AST_PTHREADT_STOP) && (monitor_thread != AST_PTHREADT_NULL)) {
		pthread_t th = monitor_thread;
		monitor_thread = AST_PTHREADT_STOP;
		pthread_cancel(th);
		pthread_kill(th, SIGURG);
		ast_mutex_unlock(&monlock);
		pthread_join(th, NULL);
	} else {
		monitor_thread = AST_PTHREADT_STOP;
		ast_mutex_unlock(&monlock);
	}
	ast_verbose("SSDP channel unloading...%d %d\n", ssdpsock, ssdpefd);
    if(ssdpsock > -1) {close(ssdpsock);}
    if(ssdpefd > -1) {close(ssdpefd);}
	return 0;
}

static int reload(void)
{
	ast_verbose("SSDP channel reloading...\n");

    ast_mutex_lock(&ssdp_reload_lock);
	if (ssdp_reloading) {
		ast_verbose("Previous SSDP reload not yet done\n");
	} else {
		ssdp_reloading = TRUE;
		ssdp_reloadreason = CHANNEL_MODULE_RELOAD;
	}
	ast_mutex_unlock(&ssdp_reload_lock);

    restart_monitor();
	return AST_MODULE_LOAD_SUCCESS;
}

AST_MODULE_INFO(ASTERISK_GPL_KEY, AST_MODFLAG_LOAD_ORDER, "SIP Server Discovery Protocol (SSDP)",
		.support_level = AST_MODULE_SUPPORT_CORE,
		.load = load_module,
		.unload = unload_module,
		.reload = reload,
		.load_pri = AST_MODPRI_CHANNEL_DRIVER,
	       );
