MAKE       := make -w
PWD        := $(shell pwd)

AZM_SDK_DIR       := $(HOME)/AZM335X_LINUX_BSP_201303
PATH              := $(PATH):$(AZM_SDK_DIR)/arm-eabi-4.4.3/bin
PATH              := $(PATH):$(AZM_SDK_DIR)/rootfs/buildroot/output/host/usr/bin
PATH              := $(PATH):$(HOME)/root/CodeSourcery/Sourcery_G++_Lite/bin
AZM_TARGET_DIR    := $(AZM_SDK_DIR)/rootfs/buildroot/output/target
AZM_SYSROOT_DIR   := $(AZM_SDK_DIR)/rootfs/buildroot/output/host/usr/arm-buildroot-linux-gnueabi/sysroot
SYSROOTS_DIR      := $(AZM_SYSROOT_DIR)
DM3730_SYSROOTS_DIR := $(HOME)/root/CodeSourcery/Sourcery_G++_Lite/arm-none-linux-gnueabi/libc
TARGET_DIR        := $(AZM_TARGET_DIR)
AZM_KERNEL_DIR    := $(AZM_SDK_DIR)/kernel
AZM_CC_PRIFIX     := arm-linux-gnueabihf-
HOST              := arm-linux-gnueabihf
DOWNLOAD_DIR      := $(HOME)/.download

LUAJIT_DIR        := $(PWD)/LuaJIT-2.0.4
PCRE_DIR          := $(PWD)/pcre-8.38
OPENSSL_DIR       := $(PWD)/openssl-1.0.1s
ZLIB_DIR          := $(PWD)/zlib-1.2.8
LUA_MODULE_DIR    := $(PWD)/lua-nginx-module-master
NGINX_DIR         := $(PWD)/nginx-1.9.12
OPENRESTY_DIR     := $(PWD)/openresty-1.9.7.4
ECHO_MODULE_DIR   := $(OPENRESTY_DIR)/bundle/echo-nginx-module-0.58
PHP_DIR           := $(PWD)/php-7.0.4

ASTERISK_DIR      := $(PWD)/asterisk-13.11.2
ASTERISK_GUI_DIR  := $(PWD)/asterisk-gui-2.0
LIBPRI_DIR        := $(PWD)/libpri-1.5.0
DAHDI_LINUX_DIR   := $(PWD)/dahdi-linux-2.11.1
DAHDI_TOOLS_DIR   := $(PWD)/dahdi-tools-2.11.1
PJPROJECT_DIR     := $(PWD)/pjproject-2.4.5

ASTERISK_CN_SOUND_DIR := $(PWD)/asterisk-core-sounds-cn-gsm

LSQLITE3_DIR      := $(PWD)/lsqlite3_fsl09w
LBIT_DIR          := $(PWD)/LuaBitOp-1.0.2
JSON4LUA_DIR      := $(PWD)/json4lua-0.9.50

SIPP_DIR          := $(PWD)/sipp-3.5.1

OSIP_DIR          := $(PWD)/libosip2-5.0.0
EXOSIP_DIR        := $(PWD)/libexosip2-5.0.0

LIBPCAP_DIR       := $(PWD)/libpcap
TCPDUMP_DIR       := $(PWD)/tcpdump

define download
	@if [ ! -d  $(DOWNLOAD_DIR) ];then mkdir $(DOWNLOAD_DIR);fi; \
	if [ -f $(DOWNLOAD_DIR)/$(2).tmp ];then rm $(DOWNLOAD_DIR)/$(2).tmp;fi; \
	if [ ! -f $(DOWNLOAD_DIR)/$(2) ] ;then \
		echo "download "$(2); \
		if [ -x /usr/bin/wget ];then wget -O $(DOWNLOAD_DIR)/$(2).tmp $(3); \
		else echo "please install wget";fi;fi; \
	if [ -f $(DOWNLOAD_DIR)/$(2).tmp ];then mv $(DOWNLOAD_DIR)/$(2).tmp $(DOWNLOAD_DIR)/$(2);fi; \
	if [ -f $(DOWNLOAD_DIR)/$(2) ] && [ ! -d $(1) ];then \
		echo "unpack "$(2); \
		if [ ! -z $(filter %.tar.gz, $(2)) ];then tar xzf $(DOWNLOAD_DIR)/$(2);fi; \
		if [ ! -z $(filter %.tar.bz2, $(2)) ];then tar xjf $(DOWNLOAD_DIR)/$(2);fi; \
		if [ ! -z $(filter %.zip, $(2)) ];then unzip $(DOWNLOAD_DIR)/$(2);fi; \
	fi;
endef

debian:debian-nginx-install debian-php-install debian-lua-module-install debian-rootfs-install

debian-nginx:
	$(MAKE) -C $(LUAJIT_DIR)
	$(MAKE) -C $(LUAJIT_DIR) install
	if [ ! -f $(NGINX_DIR)/Makefile ];then cd $(NGINX_DIR) && ./configure --with-pcre=$(PCRE_DIR) --with-openssl=$(OPENSSL_DIR) --with-zlib=$(ZLIB_DIR) \
		--add-module=$(LUA_MODULE_DIR) --add-module=$(ECHO_MODULE_DIR) --with-ipv6;fi
	$(MAKE) -C $(NGINX_DIR)

debian-nginx-install:debian-nginx
	if [ ! -d /usr/local/sbin ];then mkdir -p /usr/local/sbin;fi
	cp -rf $(NGINX_DIR)/objs/nginx /usr/local/sbin/nginx
	if [ ! -d /usr/local/nginx/logs ];then mkdir -p /usr/local/nginx/logs;fi
	if [ ! -d /usr/local/nginx/conf ];then mkdir -p /usr/local/nginx/conf;fi
	cp -rf $(NGINX_DIR)/conf/* /usr/local/nginx/conf/
	cp -rf $(PWD)/nginx-config/conf/* /usr/local/nginx/conf/

debian-php:
	if [ ! -f $(PHP_DIR)/Makefile ];then cd $(PHP_DIR) && ./configure --enable-fpm \
		--disable-all --disable-cli --disable-cgi --disable-phpdbg \
		--with-sqlite3 --enable-session --enable-json --enable-filter \
		--enable-pdo --with-pdo-mysql --with-openssl --enable-hash;fi
	$(MAKE) -C $(PHP_DIR)

debian-php-install:debian-php
	if [ ! -d /usr/local/etc/php-fpm.d ];then mkdir -p /usr/local/etc/php-fpm.d;fi
	if [ ! -d /usr/local/var/log ];then mkdir -p /usr/local/var/log;fi
	cp -rf $(PHP_DIR)/sapi/fpm/php-fpm /usr/local/sbin/php-fpm
	cp -rf $(PWD)/php-config/sapi/fpm/php-fpm.conf /usr/local/etc/php-fpm.conf
	cp -rf $(PWD)/php-config/sapi/fpm/www.conf /usr/local/etc/php-fpm.d/www.conf

debian-pjproject:
	if [ ! -f $(PJPROJECT_DIR)/config.log ];then cd $(PJPROJECT_DIR) && ./configure --prefix=/usr --enable-shared;fi
	$(MAKE) -C $(PJPROJECT_DIR) dep
	$(MAKE) -C $(PJPROJECT_DIR)

debian-pjproject-install:debian-pjproject
	$(MAKE) -C $(PJPROJECT_DIR) install

debian-dahdi-linux:
	$(MAKE) -C $(DAHDI_LINUX_DIR)

debian-dahdi-linux-install:debian-dahdi-linux
	$(MAKE) -C $(DAHDI_LINUX_DIR) install-modules
	$(MAKE) -C $(DAHDI_LINUX_DIR) install-include

debian-dahdi-tools:debian-dahdi-linux-install
	if [ ! -f $(DAHDI_TOOLS_DIR)/Makefile ];then cd $(DAHDI_TOOLS_DIR) && ./configure \
		--with-dahdi=$(DAHDI_LINUX_DIR);fi
	$(MAKE) -C $(DAHDI_TOOLS_DIR)

debian-dahdi-tools-install:debian-dahdi-tools
	if [ ! -f $(DAHDI_TOOLS_DIR)/xpp/dahdi_genconf.8 ];then cp -rf $(PWD)/asterisk/dahdi_genconf.8 $(DAHDI_TOOLS_DIR)/xpp;fi
	$(MAKE) -C $(DAHDI_TOOLS_DIR) install

debian-libpri:
	$(MAKE) -C $(LIBPRI_DIR)

debian-libpri-install:debian-libpri
	$(MAKE) -C $(LIBPRI_DIR) install

debian-asterisk:debian-pjproject-install debian-dahdi-tools-install debian-libpri-install
	cp -rf $(PWD)/asterisk/menuselect.makeopts.debian $(ASTERISK_DIR)/menuselect.makeopts
	cp -rf $(PWD)/asterisk/app_voicemail.c $(ASTERISK_DIR)/apps/app_voicemail.c
	if [ ! -f $(ASTERISK_DIR)/config.log ];then cp -rf $(PWD)/asterisk/asterisk_configure $(ASTERISK_DIR)/configure; \
		cd $(ASTERISK_DIR) && ./configure;fi
	$(MAKE) -C $(ASTERISK_DIR)

debian-asterisk-install:debian-asterisk
	$(MAKE) -C $(ASTERISK_DIR) install
	$(MAKE) -C $(ASTERISK_DIR) samples

debian-asterisk-module:
	gcc -I/usr/include/lua5.1 -I$(PWD)/asterisk-13.11.2/include -fPIC -shared -o func_lua.so $(PWD)/asterisk/func_lua.c

debian-asterisk-module-install:debian-asterisk-module

debian-asterisk-gui:debian-asterisk-install
	if [ ! -f $(ASTERISK_GUI_DIR)/config.log ];then cd $(ASTERISK_GUI_DIR) && ./configure;fi
	$(MAKE) -C $(ASTERISK_GUI_DIR)

debian-asterisk-gui-install:debian-asterisk-gui
	$(MAKE) -C $(ASTERISK_GUI_DIR) install

debian-lua-module:
	gcc -fPIC -shared -o $(LSQLITE3_DIR)/lsqlite3.so $(LSQLITE3_DIR)/lsqlite3.c -llua5.1 -lsqlite3 -I/usr/include/lua5.1
	gcc -fPIC -shared -o $(LBIT_DIR)/bit.so $(LBIT_DIR)/bit.c -llua5.1 -I/usr/include/lua5.1
	gcc -fPIC -shared -o $(PWD)/lua/llinux.so $(PWD)/lua/llinux.c -llua5.1 -I/usr/include/lua5.1
	gcc -fPIC -shared -o $(PWD)/lua/lepoll.so $(PWD)/lua/lepoll.c -llua5.1 -I/usr/include/lua5.1
	gcc -fPIC -shared -o $(PWD)/lua/luart.so $(PWD)/lua/luart.c -llua5.1 -I/usr/include/lua5.1

debian-lua-module-install:debian-lua-module
	if [ ! -d /usr/lib/lua/5.1 ];then mkdir -p /usr/lib/lua/5.1;fi
	cp -rf $(LSQLITE3_DIR)/lsqlite3.so /usr/lib/lua/5.1
	cp -rf $(LBIT_DIR)/bit.so /usr/lib/lua/5.1
	cp -rf $(PWD)/lua/llinux.so /usr/lib/lua/5.1
	cp -rf $(PWD)/lua/lepoll.so /usr/lib/lua/5.1
	cp -rf $(PWD)/lua/luart.so /usr/lib/lua/5.1
	cp -rf $(JSON4LUA_DIR)/json/json.lua /usr/local/share/lua/5.1

debian-asterisk-sound-install:
	if [ ! -d /var/lib/asterisk/sounds/cn ];then mkdir -p /var/lib/asterisk/sounds/cn;fi
	cp -rf $(ASTERISK_CN_SOUND_DIR)/* /var/lib/asterisk/sounds/cn/

debian-python-ext-install:
	if [ ! -d /var/www/html ];then mkdir -p /var/www/html;fi
	if [ ! -d /var/www/python ];then mkdir -p /var/www/python;fi
	if [ ! -d /etc/supervisor ];then mkdir /etc/supervisor;fi
	if [ ! -f /etc/supervisor/supervisord.conf ];then cp -rf $(PWD)/web-api/supervisord.conf /etc/supervisor/supervisord.conf;fi
	if [ ! -d /etc/supervisor/conf.d ];then mkdir -p /etc/supervisor/conf.d; \
		cp -rf $(PWD)/web-api/officelink.ini /etc/supervisor/conf.d; \
	fi
	if [ ! -f /usr/local/officelink/bin/activate ];then rm -rf /usr/local/officelink;fi
	if [ ! -f /usr/local/officelink/bin/activate ];then \
		virtualenv --no-site-packages -p python3 /usr/local/officelink; \
		/usr/local/officelink/bin/pip install -r $(PWD)/requirements.txt; \
	fi
	cp -rf $(PWD)/web-api/*.py /var/www/python

debian-flight-install:
	if [ ! -d /var/www/php ];then mkdir -p /var/www/php;fi
	cp -rf $(PWD)/flight/flight /var/www/php
	cp -rf $(PWD)/web-api/*.php /var/www/php

debian-rootfs-install:debian-asterisk-gui-install debian-asterisk-sound-install debian-python-ext-install
	cp -rf $(PWD)/rootfs/* /
	cp -rf $(PWD)/rootfs-debian/* /
	cp -rf $(PWD)/VERSION /etc

define localinstall
	cp -r $(PWD)/lua/conf_* /usr/bin/; \
	cp -r $(PWD)/lua/json.lua /usr/local/share/lua/5.1/; \
	cp -r $(PWD)/nginx-config/conf/nginx.conf /usr/local/nginx/conf/; \
	cp -r $(PWD)/rootfs/* /; \
	cp -rf $(PWD)/rootfs-debian/* /;\
	if [ ! -d  $(PWD)/officelink-gui ];then git clone git@192.168.1.254:officelink/officelink-gui.git officelink-gui;fi; \
	if [ -d $(PWD)/officelink-gui ];then cd $(PWD)/officelink-gui && git pull origin master;fi; \
	if [ -d $(PWD)/officelink-gui ];then cp -r $(PWD)/officelink-gui/* /var/www/;fi;
endef

debian-install:
	$(call localinstall)

debian-setup:
	apt-get install -y wget unzip subversion git-core build-essential linux-headers-$(shell uname -r) libncurses5-dev uuid-dev libjansson-dev libxml2-dev sqlite3 libsqlite3-dev lua5.1 liblua5.1-dev u-boot-tools gettext texinfo bison flex lib32z1 lib32ncurses5 lib32c++
	apt-get install -y fail2ban python3 python-pip mysql-client
	apt-get install -y libssl-dev libsctp-dev libpcap-dev
	apt-get install -y tftpd-hpa tftp-hpa vsftpd portmap nfs-kernel-server nfs-common
	pip install virtualenv supervisor

debian-sipp:
	if [ ! -f $(SIPP_DIR)/Makefile ];then cd $(SIPP_DIR) && ./configure --with-openssl --with-pcap --with-sctp;fi
	$(MAKE) -C $(SIPP_DIR)
	$(MAKE) -C $(SIPP_DIR) install

dm3730:download
	$(MAKE) -C $(LUAJIT_DIR) HOST_CC="gcc -m32" CROSS=arm-none-linux-gnueabi- \
		TARGET_CFLAGS="-mcpu=cortex-a8 -mfloat-abi=softfp" CFLAGS="-DLUAJIT_NO_LOG2 -DLUAJIT_NO_EXP2"
	$(MAKE) -C $(LUAJIT_DIR) install DESTDIR=$(LUAJIT_DIR)
	if [ ! -f $(NGINX_DIR)/Makefile ];then cd $(NGINX_DIR) && ./configure --with-cc=arm-none-linux-gnueabi-gcc \
		--with-cpp=arm-none-linux-gnueabi-g++ --with-cpu-opt=arm \
		--with-pcre=$(PCRE_DIR) --with-openssl=$(OPENSSL_DIR) --with-zlib=$(ZLIB_DIR) \
		--add-module=$(LUA_MODULE_DIR) --add-module=$(ECHO_MODULE_DIR) --with-ipv6;fi
	$(MAKE) -C $(NGINX_DIR)
	if [ ! -f $(PHP_DIR)/Makefile ];then cd $(PHP_DIR) && ./configure --host=arm-linux --enable-fpm \
		--disable-all --disable-cli --disable-cgi --disable-phpdbg CC=arm-none-linux-gnueabi-gcc --enable-session --enable-json;fi
	$(MAKE) -C $(PHP_DIR)

am335x:am335x-nginx-install am335x-php-install am335x-asterisk-install am335x-lua-module-install am335x-asterisk-sound-install am335x-officelink-gui-install am335x-rootfs-install

am335x-nginx:
	cp -rf $(PWD)/nginx-config/* $(NGINX_DIR)
	cp -rf $(PWD)/php-config/* $(PHP_DIR)
	$(MAKE) -C $(LUAJIT_DIR) HOST_CC="gcc -m32" CROSS=arm-linux-gnueabihf- \
		TARGET_CFLAGS="-mcpu=cortex-a8" CFLAGS="-DLUAJIT_NO_LOG2 -DLUAJIT_NO_EXP2"
	$(MAKE) -C $(LUAJIT_DIR) install DESTDIR=$(AZM_SYSROOT_DIR)
	if [ ! -f $(NGINX_DIR)/Makefile ];then cd $(NGINX_DIR) && ./configure --with-cc=arm-linux-gnueabihf-gcc \
		--with-cpp=arm-linux-gnueabihf-g++ --with-cpu-opt=arm --with-cc-opt=-DNGX_HAVE_ACCEPT4=0\
		--with-pcre=$(PCRE_DIR) --with-openssl=$(OPENSSL_DIR) --with-zlib=$(ZLIB_DIR) \
		--add-module=$(LUA_MODULE_DIR) --add-module=$(ECHO_MODULE_DIR) --with-ipv6;fi
	$(MAKE) -C $(NGINX_DIR)
	arm-linux-gnueabihf-strip $(NGINX_DIR)/objs/nginx

am335x-nginx-install:am335x-nginx
	cp -rf $(AZM_SYSROOT_DIR)/usr/local/lib/libluajit-5.1.so.2.0.4 $(AZM_TARGET_DIR)/usr/lib/libluajit-5.1.so.2
	if [ ! -d $(AZM_TARGET_DIR)/usr/local/sbin ];then mkdir -p $(AZM_TARGET_DIR)/usr/local/sbin;fi
	cp -rf $(NGINX_DIR)/objs/nginx $(AZM_TARGET_DIR)/usr/local/sbin/nginx
	if [ ! -d $(AZM_TARGET_DIR)/usr/local/nginx/logs ];then mkdir -p $(AZM_TARGET_DIR)/usr/local/nginx/logs;fi
	if [ ! -d $(AZM_TARGET_DIR)/usr/local/nginx/conf ];then mkdir -p $(AZM_TARGET_DIR)/usr/local/nginx/conf;fi
	cp -rf $(NGINX_DIR)/conf/* $(AZM_TARGET_DIR)/usr/local/nginx/conf/

am335x-php:
	if [ ! -f $(PHP_DIR)/Makefile ];then cd $(PHP_DIR) && ./configure --host=arm-linux --enable-fpm \
		--disable-all --disable-cli --disable-cgi --disable-phpdbg --with-sqlite3 CC=arm-linux-gnueabihf-gcc LIBS=-ldl --enable-session --enable-json --enable-filter;fi
	$(MAKE) -C $(PHP_DIR)
	arm-linux-gnueabihf-strip $(PHP_DIR)/sapi/fpm/php-fpm

am335x-php-install:am335x-php
	if [ ! -d $(AZM_TARGET_DIR)/usr/local/etc/php-fpm.d ];then mkdir -p $(AZM_TARGET_DIR)/usr/local/etc/php-fpm.d;fi
	if [ ! -d $(AZM_TARGET_DIR)/usr/local/var/log ];then mkdir -p $(AZM_TARGET_DIR)/usr/local/var/log;fi
	cp -rf $(PHP_DIR)/sapi/fpm/php-fpm $(AZM_TARGET_DIR)/usr/local/sbin/php-fpm
	cp -rf $(PWD)/php-config/sapi/fpm/php-fpm.conf $(AZM_TARGET_DIR)/usr/local/etc/php-fpm.conf
	cp -rf $(PWD)/php-config/sapi/fpm/www.conf $(AZM_TARGET_DIR)/usr/local/etc/php-fpm.d/www.conf

am335x-asterisk:
	cp -rf $(PWD)/asterisk/menuselect.makeopts $(ASTERISK_DIR)
	cp -rf $(PWD)/asterisk/app_voicemail.c $(ASTERISK_DIR)/apps/app_voicemail.c
	if [ ! -f $(PJPROJECT_DIR)/config.log ];then cd $(PJPROJECT_DIR) && ./configure --host=arm-linux-gnueabihf --prefix=/usr --enable-shared --with-ssl=$(OPENSSL_DIR);fi
	$(MAKE) -C $(PJPROJECT_DIR) dep
	$(MAKE) -C $(PJPROJECT_DIR)
	$(MAKE) -C $(PJPROJECT_DIR) install DESTDIR=$(AZM_SYSROOT_DIR)
	$(MAKE) -C $(DAHDI_LINUX_DIR) KSRC=$(AZM_KERNEL_DIR) CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(DAHDI_LINUX_DIR) install-include KSRC=$(AZM_KERNEL_DIR) DESTDIR=$(AZM_SYSROOT_DIR) CROSS_COMPILE=arm-eabi- ARCH=arm
	
	if [ ! -f $(DAHDI_TOOLS_DIR)/Makefile ];then cd $(DAHDI_TOOLS_DIR) && ./configure --host=arm-linux-gnueabihf \
		--with-dahdi=$(DAHDI_LINUX_DIR);fi
	$(MAKE) -C $(DAHDI_TOOLS_DIR)
	$(MAKE) -C $(DAHDI_TOOLS_DIR) install DESTDIR=$(AZM_SYSROOT_DIR)
	$(MAKE) -C $(LIBPRI_DIR) CC=arm-linux-gnueabihf-gcc
	$(MAKE) -C $(LIBPRI_DIR) install CC=arm-linux-gnueabihf-gcc DESTDIR=$(AZM_SYSROOT_DIR)
	if [ ! -f $(ASTERISK_DIR)/config.log ];then cp -rf $(PWD)/asterisk/asterisk_configure $(ASTERISK_DIR)/configure; \
		cd $(ASTERISK_DIR) && ./configure --host=arm-linux-gnueabihf;fi
	$(MAKE) -C $(ASTERISK_DIR)
	$(MAKE) -C $(ASTERISK_DIR) install DESTDIR=$(AZM_SYSROOT_DIR)
	@#if [ ! -f $(ASTERISK_GUI_DIR)/config.log ];then cd $(ASTERISK_GUI_DIR) && ./configure --host=arm-linux-gnueabihf;fi
	@#$(MAKE) -C $(ASTERISK_GUI_DIR)

am335x-asterisk-install:am335x-asterisk
	$(MAKE) -C $(PJPROJECT_DIR) install DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(DAHDI_LINUX_DIR) install-modules KSRC=$(AZM_KERNEL_DIR) DESTDIR=$(AZM_TARGET_DIR) CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(DAHDI_TOOLS_DIR) install DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(LIBPRI_DIR) install CC=arm-linux-gnueabihf-gcc DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(ASTERISK_DIR) install DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(ASTERISK_DIR) samples DESTDIR=$(AZM_TARGET_DIR)
	rm -rf $(AZM_TARGET_DIR)/etc/asterisk/extensions.ael
	rm -rf $(AZM_TARGET_DIR)/etc/asterisk/extensions.lua
	rm -rf $(AZM_TARGET_DIR)/etc/asterisk/extensions_minivm.conf
	@#$(MAKE) -C $(ASTERISK_GUI_DIR) install DESTDIR=$(AZM_TARGET_DIR)

am335x-asterisk-uninstall:
	$(MAKE) -C $(ASTERISK_DIR) uninstall DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(PJPROJECT_DIR) uninstall DESTDIR=$(AZM_TARGET_DIR)
	$(MAKE) -C $(DAHDI_LINUX_DIR) uninstall-modules KSRC=$(AZM_KERNEL_DIR) DESTDIR=$(AZM_TARGET_DIR) CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(DAHDI_TOOLS_DIR) uninstall DESTDIR=$(AZM_TARGET_DIR)

am335x-asterisk-alone:
	if [ ! -f $(ASTERISK_DIR)/config.log ];then cp -rf $(PWD)/asterisk/asterisk_configure $(ASTERISK_DIR)/configure; \
		cd $(ASTERISK_DIR) && ./configure --host=arm-linux-gnueabihf;fi
	cp -rf $(PWD)/asterisk/menuselect.makeopts $(ASTERISK_DIR)
	cp -rf $(PWD)/asterisk/app_voicemail.c $(ASTERISK_DIR)/apps/app_voicemail.c
	$(MAKE) -C $(ASTERISK_DIR)

am335x-lua-module:
	$(AZM_CC_PRIFIX)gcc -fPIC -shared -o $(LSQLITE3_DIR)/lsqlite3.so $(LSQLITE3_DIR)/lsqlite3.c -llua -lsqlite3
	$(AZM_CC_PRIFIX)gcc -fPIC -shared -o $(LBIT_DIR)/bit.so $(LBIT_DIR)/bit.c -llua
	$(AZM_CC_PRIFIX)gcc -fPIC -shared -o $(PWD)/lua/llinux.so $(PWD)/lua/llinux.c -lrt -llua
	$(AZM_CC_PRIFIX)gcc -fPIC -shared -o $(PWD)/lua/lepoll.so $(PWD)/lua/lepoll.c -llua
	$(AZM_CC_PRIFIX)gcc -fPIC -shared -o $(PWD)/lua/luart.so $(PWD)/lua/luart.c -llua

am335x-lua-module-install:am335x-lua-module
	if [ ! -d $(AZM_TARGET_DIR)/usr/lib/lua ];then mkdir -p $(AZM_TARGET_DIR)/usr/lib/lua;fi
	cp -rf $(LSQLITE3_DIR)/lsqlite3.so $(AZM_TARGET_DIR)/usr/lib/lua
	cp -rf $(LBIT_DIR)/bit.so $(AZM_TARGET_DIR)/usr/lib/lua
	cp -rf $(PWD)/lua/llinux.so $(AZM_TARGET_DIR)/usr/lib/lua
	cp -rf $(PWD)/lua/lepoll.so $(AZM_TARGET_DIR)/usr/lib/lua
	cp -rf $(PWD)/lua/luart.so $(AZM_TARGET_DIR)/usr/lib/lua
	if [ ! -d $(AZM_TARGET_DIR)/usr/bin ];then mkdir -p $(AZM_TARGET_DIR)/usr/bin;fi
	if [ ! -d $(AZM_TARGET_DIR)/usr/share/lua ];then mkdir -p $(AZM_TARGET_DIR)/usr/share/lua;fi
	cp -rf $(PWD)/lua/led.lua $(AZM_TARGET_DIR)/usr/bin
	cp -rf $(PWD)/lua/monitor.lua $(AZM_TARGET_DIR)/usr/bin
	cp -rf $(PWD)/lua/conf_*.lua $(AZM_TARGET_DIR)/usr/bin
	cp -rf $(JSON4LUA_DIR)/json/json.lua $(AZM_TARGET_DIR)/usr/share/lua

am335x-lua-module-clean:
	rm -rf $(PWD)/lua/*.so

am335x-asterisk-sound-install:
	if [ ! -d $(AZM_TARGET_DIR)/var/lib/asterisk/sounds/cn ];then mkdir -p $(AZM_TARGET_DIR)/var/lib/asterisk/sounds/cn;fi
	cp -rf $(ASTERISK_CN_SOUND_DIR)/* $(AZM_TARGET_DIR)/var/lib/asterisk/sounds/cn/

am335x-officelink-gui-install:
	if [ ! -d $(AZM_TARGET_DIR)/var/www ];then mkdir -p $(AZM_TARGET_DIR)/var/www;fi
	if [ ! -d  $(PWD)/officelink-gui ];then git clone git@192.168.1.254:officelink/officelink-gui.git officelink-gui;fi;
	cp -rf $(PWD)/officelink-gui/* $(AZM_TARGET_DIR)/var/www/
	cp -rf $(PWD)/dustbin/avatar100.png $(AZM_TARGET_DIR)/var/www/html/img/
	cp -rf $(PWD)/dustbin/avatar130.png  $(AZM_TARGET_DIR)/var/www/html/img/

am335x-rootfs-install:
	if [ ! -d $(AZM_TARGET_DIR)/root/.ssh ];then mkdir -p $(AZM_TARGET_DIR)/root/.ssh;fi
	cat $(HOME)/.ssh/id_rsa.pub > $(AZM_TARGET_DIR)/root/.ssh/authorized_keys
	cp -rf $(PWD)/rootfs/* $(AZM_TARGET_DIR)/
	cp -rf $(PWD)/rootfs-am335x/* $(AZM_TARGET_DIR)/
	cp -rf $(PWD)/rootfs-am335x/etc/inittab $(AZM_SDK_DIR)/rootfs/system/inittab
	cp -rf $(PWD)/rootfs-am335x/etc/inittab $(AZM_SDK_DIR)/rootfs/buildroot/system/inittab
	cp -rf $(PWD)/VERSION $(AZM_TARGET_DIR)/etc

am335x-sdk-install:
	if [ ! -d  $(HOME)/AZM335X_LINUX_BSP_201303 ];then tar xjf $(DOWNLOAD_DIR)/AZM335X_LINUX_BSP_201303.tar.bz2 -C $(HOME); \
		tar xjf $(DOWNLOAD_DIR)/AZM335X_LINUX_BSP_201303.Patch.tar.bz2 -C $(HOME); \
		cp -rf $(HOME)/AZM335X_LINUX_BSP_201303.Patch/* $(HOME)/AZM335X_LINUX_BSP_201303/; \
		tar xjf $(HOME)/AZM335X_LINUX_BSP_201303/tools/arm-eabi-4.4.3.tar.bz2 -C $(HOME)/AZM335X_LINUX_BSP_201303;fi

am335x-rootfs:
	if [ ! -d $(AZM_SDK_DIR)/rootfs/buildroot ];then \
		if [ -d $(DOWNLOAD_DIR)/dl ];then cp -rf $(DOWNLOAD_DIR)/dl/* $(AZM_SDK_DIR)/rootfs/dl/;fi; \
		cd $(AZM_SDK_DIR)/rootfs;$(MAKE) cleanbuild;fi
	cp -rf $(PWD)/homeserver_config $(AZM_SDK_DIR)/rootfs/buildroot/.config
	cp -rf $(PWD)/package/* $(AZM_SDK_DIR)/rootfs/buildroot/package/
	$(MAKE) -C $(AZM_SDK_DIR)/rootfs/buildroot
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(AZM_SDK_DIR)/rootfs/buildroot/output/images/rootfs.ext2 $(PWD)/sdcard/rootfs.ext2

am335x-kernel:
	cp -rf $(PWD)/homeserver_kernel_config $(AZM_SDK_DIR)/kernel/.config
	cp -rf $(PWD)/am335x/kernel/am33xx.h $(AZM_KERNEL_DIR)/arch/arm/plat-omap/include/plat/am33xx.h
	cp -rf $(PWD)/am335x/kernel/control.h $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/control.h
	cp -rf $(PWD)/am335x/kernel/board-am335xevm.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/board-am335xevm.c
	cp -rf $(PWD)/am335x/kernel/mux33xx.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/mux33xx.c
	cp -rf $(PWD)/am335x/kernel/devices.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/devices.c
	cp -rf $(PWD)/am335x/kernel/leds-officelink.c $(AZM_KERNEL_DIR)/drivers/leds/leds-officelink.c
	cp -rf $(PWD)/am335x/kernel/rtc-pcf8563.c $(AZM_KERNEL_DIR)/drivers/rtc/rtc-pcf8563.c
	cp -rf $(PWD)/am335x/kernel/Makefile.leds $(AZM_KERNEL_DIR)/drivers/leds/Makefile
	$(MAKE) -C $(AZM_SDK_DIR)/kernel uImage CROSS_COMPILE=arm-eabi- ARCH=arm
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(AZM_SDK_DIR)/kernel/arch/arm/boot/uImage $(PWD)/sdcard/uImage

am335x-kernel-eth-master:
	cp -rf $(PWD)/homeserver_kernel_config $(AZM_SDK_DIR)/kernel/.config
	cp -rf $(PWD)/am335x/kernel/control-eth-master.h $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/control.h
	cp -rf $(PWD)/am335x/kernel/board-am335xevm.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/board-am335xevm.c
	cp -rf $(PWD)/am335x/kernel/mux33xx.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/mux33xx.c
	cp -rf $(PWD)/am335x/kernel/devices.c $(AZM_KERNEL_DIR)/arch/arm/mach-omap2/devices.c
	cp -rf $(PWD)/am335x/kernel/leds-officelink.c $(AZM_KERNEL_DIR)/drivers/leds/leds-officelink.c
	cp -rf $(PWD)/am335x/kernel/rtc-pcf8563.c $(AZM_KERNEL_DIR)/drivers/rtc/rtc-pcf8563.c
	cp -rf $(PWD)/am335x/kernel/Makefile.leds $(AZM_KERNEL_DIR)/drivers/leds/Makefile
	$(MAKE) -C $(AZM_SDK_DIR)/kernel uImage CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/kernel/arch/arm/boot/uImage $(PWD)/uImage

am335x-kernel-config:
	$(MAKE) -C $(AZM_SDK_DIR)/kernel menuconfig CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/kernel/.config $(PWD)/homeserver_kernel_config

am335x-u-boot:
	cp -rf $(PWD)/am335x/u-boot/board.c $(AZM_SDK_DIR)/u-boot/arch/arm/lib/board.c
	cp -rf $(PWD)/am335x/u-boot/mux.c $(AZM_SDK_DIR)/u-boot/board/ti/am335x/mux.c
	cp -rf $(PWD)/am335x/u-boot/evm.c $(AZM_SDK_DIR)/u-boot/board/ti/am335x/evm.c
	cp -rf $(PWD)/am335x/u-boot/am335x_evm.h $(AZM_SDK_DIR)/u-boot/include/configs/am335x_evm.h
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot am335x_evm_config CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot clean CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	if [ ! -d $(AZM_SDK_DIR)/libazm335x_noid ];then cp -rf $(PWD)/am335x/libazm335x_noid $(AZM_SDK_DIR)/;fi
	$(MAKE) -C $(AZM_SDK_DIR)/libazm335x_noid CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/libazm335x_noid/libazm335x.lib $(AZM_SDK_DIR)/u-boot/lib/
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(AZM_SDK_DIR)/u-boot/u-boot.img $(PWD)/sdcard/u-bootn.img
	cp -rf $(AZM_SDK_DIR)/u-boot/MLO $(PWD)/sdcard/MLON
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot am335x_evm_sdboot_config CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot clean CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/u-boot/u-boot.img $(PWD)/sdcard/u-boot.img
	cp -rf $(AZM_SDK_DIR)/u-boot/MLO $(PWD)/sdcard/MLO

am335x-u-boot-eth-master:
	cp -rf $(PWD)/am335x/u-boot/board.c $(AZM_SDK_DIR)/u-boot/arch/arm/lib/board.c
	cp -rf $(PWD)/am335x/u-boot/mux.c $(AZM_SDK_DIR)/u-boot/board/ti/am335x/mux.c
	cp -rf $(PWD)/am335x/u-boot/evm-eth-master.c $(AZM_SDK_DIR)/u-boot/board/ti/am335x/evm.c
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot am335x_evm_config CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot clean CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	if [ ! -d $(AZM_SDK_DIR)/libazm335x_noid ];then cp -rf $(PWD)/am335x/libazm335x_noid $(AZM_SDK_DIR)/;fi
	$(MAKE) -C $(AZM_SDK_DIR)/libazm335x_noid CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/libazm335x_noid/libazm335x.lib $(AZM_SDK_DIR)/u-boot/lib/
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/u-boot/u-boot.img $(PWD)/u-bootn.img
	cp -rf $(AZM_SDK_DIR)/u-boot/MLO $(PWD)/MLON
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot am335x_evm_sdboot_config CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot clean CROSS_COMPILE=arm-eabi- ARCH=arm
	$(MAKE) -C $(AZM_SDK_DIR)/u-boot CROSS_COMPILE=arm-eabi- ARCH=arm
	cp -rf $(AZM_SDK_DIR)/u-boot/u-boot.img $(PWD)/u-boot.img
	cp -rf $(AZM_SDK_DIR)/u-boot/MLO $(PWD)/MLO

am335x-ramdisk-220:
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(DOWNLOAD_DIR)/officelink/rootfs220.ext2.back $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	rm -rf $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz
	gzip -9 $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	mkimage -A arm -C gzip -O linux -T ramdisk -a 0x82000000 -n "Linux ramdisk" -d $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz $(PWD)/sdcard/rootfs.ext2.gz.img

am335x-ramdisk-256:
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(DOWNLOAD_DIR)/officelink/rootfs256.ext2.back $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	rm -rf $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz
	gzip -9 $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	mkimage -A arm -C gzip -O linux -T ramdisk -a 0x82000000 -n "Linux ramdisk" -d $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz $(PWD)/sdcard/rootfs.ext2.gz.img

am335x-ramdisk-512:
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(DOWNLOAD_DIR)/officelink/rootfs512.ext2.back $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	rm -rf $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz
	gzip -9 $(DOWNLOAD_DIR)/officelink/rootfs.ext2
	mkimage -A arm -C gzip -O linux -T ramdisk -a 0x82000000 -n "Linux ramdisk" -d $(DOWNLOAD_DIR)/officelink/rootfs.ext2.gz $(PWD)/sdcard/rootfs.ext2.gz.img

am335x-sdcard:am335x-ramdisk-220 am335x-u-boot am335x-kernel am335x-rootfs
	$(MAKE) am335x
	$(MAKE) am335x-rootfs
	if [ ! -d $(PWD)/sdcard ];then mkdir -p $(PWD)/sdcard;fi
	cp -rf $(DOWNLOAD_DIR)/officelink/uEnv.txt $(PWD)/sdcard
	cp -rf $(PWD)/VERSION $(PWD)/sdcard

am335x-sdcard-install:
	if [ -d /tmp/boot ];then rm -rf /tmp/boot;fi
	cp -rf $(PWD)/sdcard /tmp/boot
	$(PWD)/am335x/create-sdcard.sh

am335x-sdcard-clean:
	rm -rf $(PWD)/sdcard

am335x-osip:
	if [ ! -f $(OSIP_DIR)/Makefile ];then cd $(OSIP_DIR) && ./configure --host=$(HOST) --prefix=/usr \
		--enable-pthread=no --enable-mt=no;fi
	$(MAKE) -C $(OSIP_DIR)

am335x-osip-install:am335x-osip
	if [ ! -d $(TARGET_DIR)/usr/lib ];then mkdir -p $(TARGET_DIR)/usr/lib;fi
	$(MAKE) DESTDIR=$(SYSROOTS_DIR) -C $(OSIP_DIR) install
	cp -rf $(SYSROOTS_DIR)/usr/lib/libosip2.so.12.0.0 $(TARGET_DIR)/usr/lib/libosip2.so.12
	cp -rf $(SYSROOTS_DIR)/usr/lib/libosipparser2.so.12.0.0 $(TARGET_DIR)/usr/lib/libosipparser2.so.12
	$(HOST)-strip $(TARGET_DIR)/usr/lib/libosip2.so.12
	$(HOST)-strip $(TARGET_DIR)/usr/lib/libosipparser2.so.12

am335x-exosip:am335x-osip-install
	if [ ! -f $(EXOSIP_DIR)/Makefile ];then cd $(EXOSIP_DIR) && ./configure --host=$(HOST) --prefix=/usr \
		--enable-pthread=no --enable-mt=no;fi
	$(MAKE) -C $(EXOSIP_DIR)

am335x-exosip-install:am335x-exosip
	if [ ! -d $(TARGET_DIR)/usr/lib ];then mkdir -p $(TARGET_DIR)/usr/lib;fi
	if [ ! -d $(TARGET_DIR)/usr/bin ];then mkdir -p $(TARGET_DIR)/usr/bin;fi
	$(MAKE) DESTDIR=$(SYSROOTS_DIR) -C $(EXOSIP_DIR) install
	cp -rf $(EXOSIP_DIR)/src/.libs/libeXosip2.so.12.0.0 $(TARGET_DIR)/usr/lib/libeXosip2.so.12
	cp -rf $(SYSROOTS_DIR)/lib/libresolv-0.9.34-git.so $(TARGET_DIR)/usr/lib/libresolv.so.0
	cp -rf $(SYSROOTS_DIR)/usr/lib/libssl.so.1.0.0 $(TARGET_DIR)/usr/lib/libssl.so.1.0.0
	$(HOST)-strip $(TARGET_DIR)/usr/lib/libeXosip2.so.12

PHONY += libpcap
libpcap:
	if [ ! -f $(LIBPCAP_DIR)/Makefile ];then cd $(LIBPCAP_DIR) && ./configure --host=arm-none-linux-gnueabi --with-pcap=linux;fi
	$(MAKE) -C $(LIBPCAP_DIR)
	#if [ ! -d $(TARGET_DIR)/usr/lib ];then mkdir -p $(TARGET_DIR)/usr/lib;fi
	cp -rf $(LIBPCAP_DIR)/libpcap.so.1.9.0-PRE-GIT $(DM3730_SYSROOTS_DIR)/usr/lib/libpcap.so.1
	#$(HOST)-strip $(TARGET_DIR)/usr/lib/libpcap.so.1

PHONY += tcpdump
tcpdump:libpcap
	if [ ! -f $(TCPDUMP_DIR)/Makefile ];then cd $(TCPDUMP_DIR) && ./configure --host=arm-none-linux-gnueabi;fi
	$(MAKE) -C $(TCPDUMP_DIR)
	#if [ ! -d $(TARGET_DIR)/usr/lib ];then mkdir -p $(TARGET_DIR)/usr/lib;fi
	#if [ ! -d $(TARGET_DIR)/usr/bin ];then mkdir -p $(TARGET_DIR)/usr/bin;fi
	#cp -rf $(TCPDUMP_DIR)/tcpdump $(TARGET_DIR)/usr/bin/tcpdump
	#cp -rf $(SYSROOTS_DIR)/usr/lib/libdbus-1.so.3.8.8 $(TARGET_DIR)/usr/lib/libdbus-1.so.3
	arm-none-linux-gnueabi-strip $(TCPDUMP_DIR)/tcpdump

define scpinstall
	scp -r $(PWD)/VERSION $(1):/etc/; \
	scp -r $(PWD)/lua/conf_* $(1):/usr/bin; \
	scp -r $(PWD)/lua/llinux.so $(1):/usr/lib/lua/; \
	scp -r $(PWD)/lua/led.lua $(1):/usr/bin/; \
	scp -r $(PWD)/lua/monitor.lua $(1):/usr/bin/; \
	scp -r $(PWD)/lua/json.lua $(1):/usr/share/lua/; \
	scp -r $(PWD)/nginx-config/conf/nginx.conf $(1):/usr/local/nginx/conf/; \
	if [ ! -d $(PWD)/rootfs-am335x-remote ];then mkdir -p $(PWD)/rootfs-am335x-remote;fi; \
	cp -rf $(PWD)/rootfs/* $(PWD)/rootfs-am335x-remote/; \
	cp -rf $(PWD)/rootfs-am335x/* $(PWD)/rootfs-am335x-remote/; \
	rm -rf $(PWD)/rootfs-am335x-remote/etc/network; \
	rm -rf $(PWD)/rootfs-am335x-remote/var/lib/asterisk/realtime.sqlite3; \
	scp -r $(PWD)/rootfs-am335x-remote/* $(1):/; \
	if [ ! -d  $(PWD)/officelink-gui ];then git clone git@192.168.1.254:officelink/officelink-gui.git officelink-gui;fi; \
	if [ -d $(PWD)/officelink-gui ];then cd $(PWD)/officelink-gui && git pull origin master;fi; \
	if [ -d $(PWD)/officelink-gui ];then scp -r $(PWD)/officelink-gui/* $(1):/var/www/;fi; \
	scp $(PWD)/dustbin/avatar100.png  $(1):/var/www/html/img/; \
	scp $(PWD)/dustbin/avatar130.png  $(1):/var/www/html/img/;
endef

am335x-remote-install:
	$(call scpinstall, root@192.168.1.159)
	@#$(call scpinstall, root@192.168.1.159)
	@#$(call scpinstall, root@192.168.1.200)
	@#$(call scpinstall, root@192.168.1.227)
	@#$(call scpinstall, root@192.168.1.206)

download:
	$(call download,$(ZLIB_DIR),zlib-1.2.8.tar.gz,"http://zlib.net/zlib-1.2.8.tar.gz")
	$(call download,$(LUAJIT_DIR),LuaJIT-2.0.4.tar.gz,"http://luajit.org/download/LuaJIT-2.0.4.tar.gz")
	$(call download,$(OPENSSL_DIR),openssl-1.0.1s.tar.gz,"http://www.openssl.org/source/openssl-1.0.1s.tar.gz")
	$(call download,$(PCRE_DIR),pcre-8.38.tar.bz2,"http://liquidtelecom.dl.sourceforge.net/project/pcre/pcre/8.38/pcre-8.38.tar.bz2")
	$(call download,$(OPENRESTY_DIR),openresty-1.9.7.4.tar.gz,"https://openresty.org/download/openresty-1.9.7.4.tar.gz")
	$(call download,$(LUA_MODULE_DIR),lua-nginx-module-master.zip,"https://codeload.github.com/openresty/lua-nginx-module/zip/master")
	$(call download,$(NGINX_DIR),nginx-1.9.12.tar.gz,"http://nginx.org/download/nginx-1.9.12.tar.gz")
	$(call download,$(PHP_DIR),php-7.0.4.tar.bz2,"http://cn2.php.net/get/php-7.0.4.tar.bz2/from/this/mirror")
	$(call download,.,adminer-4.2.4.php,"https://www.adminer.org/static/download/4.2.4/adminer-4.2.4.php")
	
	$(call download,$(ASTERISK_DIR),asterisk-13.11.2.tar.gz,"http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-13.11.2.tar.gz")
	$(call download,$(LIBPRI_DIR),libpri-1.5.0.tar.gz,"http://downloads.asterisk.org/pub/telephony/libpri/libpri-1.5.0.tar.gz")
	$(call download,$(DAHDI_LINUX_DIR),dahdi-linux-2.11.1.tar.gz,"http://downloads.asterisk.org/pub/telephony/dahdi-linux/dahdi-linux-2.11.1.tar.gz")
	$(call download,$(DAHDI_TOOLS_DIR),dahdi-tools-2.11.1.tar.gz,"http://downloads.asterisk.org/pub/telephony/dahdi-tools/dahdi-tools-2.11.1.tar.gz")
	$(call download,$(PJPROJECT_DIR),pjproject-2.4.5.tar.bz2,"http://www.pjsip.org/release/2.4.5/pjproject-2.4.5.tar.bz2")
	if [ ! -d $(DOWNLOAD_DIR)/asterisk-gui-2.0 ];then \
		svn co http://svn.asterisk.org/svn/asterisk-gui/branches/2.0 $(DOWNLOAD_DIR)/asterisk-gui-2.0;fi
	if [ ! -d $(ASTERISK_GUI_DIR) ];then cp -rf $(DOWNLOAD_DIR)/asterisk-gui-2.0 $(ASTERISK_GUI_DIR);fi
	
	$(call download,$(LSQLITE3_DIR),lsqlite3_fsl09w.zip,"http://lua.sqlite.org/index.cgi/zip/lsqlite3_fsl09w.zip")
	$(call download,$(LBIT_DIR),LuaBitOp-1.0.2.tar.gz,"http://bitop.luajit.org/download/LuaBitOp-1.0.2.tar.gz")
	$(call download,$(JSON4LUA_DIR),json4lua-0.9.50.zip,"http://files.luaforge.net/releases/json/json/0.9.50/json4lua-0.9.50.zip")
	$(call download,$(ASTERISK_CN_SOUND_DIR),asterisk-core-sounds-cn-gsm.zip,"")
	@#$(call download,$(SIPP_DIR),sipp-3.5.1.tar.gz,"https://github.com/SIPp/sipp/releases/download/v3.5.1/sipp-3.5.1.tar.gz")
	@###################################################################################
	$(call download,$(OSIP_DIR),libosip2-5.0.0.tar.gz,"http://ftp.gnu.org/gnu/osip/libosip2-5.0.0.tar.gz")
	$(call download,$(EXOSIP_DIR),libexosip2-5.0.0.tar.gz,"http://download.savannah.nongnu.org/releases/exosip/libexosip2-5.0.0.tar.gz")
	@###################################################################################
	if [ ! -d  $(PWD)/flight ];then git clone git@192.168.1.254:officelink/flight.git flight;fi;
	if [ -d $(PWD)/flight ];then cd $(PWD)/flight && git pull origin master;fi;
	@###################################################################################
	if [ ! -d $(LIBPCAP_DIR) ] && [ ! -d $(DOWNLOAD_DIR)/libpcap ];then git clone https://github.com/the-tcpdump-group/libpcap.git $(DOWNLOAD_DIR)/libpcap;fi
	if [ ! -d $(LIBPCAP_DIR) ];then cp -rf $(DOWNLOAD_DIR)/libpcap $(PWD);fi
	if [ ! -d $(TCPDUMP_DIR) ] && [ ! -d $(DOWNLOAD_DIR)/tcpdump ];then git clone https://github.com/the-tcpdump-group/tcpdump.git $(DOWNLOAD_DIR)/tcpdump;fi
	if [ ! -d $(TCPDUMP_DIR) ];then cp -rf $(DOWNLOAD_DIR)/tcpdump $(PWD);fi

distclean:clean
	rm -rf $(PCRE_DIR) $(OPENSSL_DIR) $(ZLIB_DIR) $(LUA_MODULE_DIR) $(NGINX_DIR) $(OPENRESTY_DIR) $(LUAJIT_DIR) $(PHP_DIR) $(ASTERISK_DIR) $(LIBPRI_DIR) $(DAHDI_LINUX_DIR) $(DAHDI_TOOLS_DIR) $(PJPROJECT_DIR) $(ASTERISK_GUI_DIR) $(ASTERISK_CN_SOUND_DIR) $(LSQLITE3_DIR) $(LBIT_DIR) $(JSON4LUA_DIR) $(SIPP_DIR) $(OSIP_DIR) $(EXOSIP_DIR) $(PWD)/officelink-gui

clean:am335x-lua-module-clean am335x-sdcard-clean
	rm -rf $(PWD)/rootfs.ext2 $(PWD)/uImage $(PWD)/MLO $(PWD)/MLON $(PWD)/u-boot.img $(PWD)/u-bootn.img

.PHONY: $(PHONY)

