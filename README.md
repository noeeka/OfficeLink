# homeserver

## 硬件/系统

1. AM335x: CPU 720MHz 1核、内存 128M、Flash 512M

2. PC虚拟机(Debian 8.6, 也是开发环境): CPU 4.10GHz、内存 1G、硬盘 60G

3. 阿里云ECS: CPU 1.90GHz 1核、内存 1G/2G、硬盘 40G

## 软件

1. AZM335X_LINUX_BSP_201303.tar.bz2: 包括内核、根文件系统(busybox)、交叉编译器等

2. AZM335X_LINUX_BSP_201303.Patch.tar.bz2: 补丁包, 如果没有就会报错, 如果熟悉也可以手动修改

3. U-Boot SPL: am335x/libazm335x_noid (无加密芯片)

4. U-Boot: am335x/u-boot (电源灯)

5. linux内核配置: homeserver_kernel_config, 主要是iptables、双网卡支持

6. Linux驱动: am335x/kernel (呼吸灯、按键)

7. buildroot配置: homeserver_config, 额外添加项janson

8. ntpd: 时间同步服务

9. Lua: 脚本运行环境, 自定义扩展库

10. Nginx: 依赖luajit、zlib、openssl、pcre、echo-nginx-module、lua-nginx-module、buildroot部分

11. php-fpm: 只编译基本功能

12. Asterisk: 依赖libpri、dahdi-linux、dahdi-tools、pjproject、asterisk-gui、buildroot部分

13. 中文语音包: asterisk-core-sounds-cn-gsm.zip

14. 启动脚本: asterisk led monitor network nginx ntp php-fpm

## 文件/目录

| 序号 | 文件/目录                      | 描述                                                              |
|------|--------------------------------|-------------------------------------------------------------------|
| 1    | am335x                         | AM335X 平台相关 (u-boot、驱动、SD卡制作等)                        |
| 2    | asterisk                       | asterisk 编译配置相关文件                                         |
| 3    | doc                            | 项目文档                                                          |
| 4    | lua                            | lua 自定义模块                                                    |
| 5    | nginx-config                   | nginx 编译配置相关文件                                            |
| 6    | package                        | buildroot 编译配置相关文件                                        |
| 7    | php-config                     | php 编译配置相关文件                                              |
| 8    | rootfs                         | 根文件系统关键配置                                                |
| 9    | rootfs-am335x                  | AM335X 根文件系统关键配置                                         |
| 10   | rootfs-debian                  | debian 根文件系统关键配置                                         |
| 11   | test                           | 测试相关                                                          |
| 12   | .bashrc                        | Linux 环境配置文件                                                |
| 13   | .gitignore                     | Git 配置文件 (忽略特殊文件)                                       |
| 14   | .vimrc                         | vim 配置文件                                                      |
| 15   | Dockerfile                     | Docker 配置文件                                                   |
| 16   | docker-ip.sh                   | Docker IP 设置程序                                                |
| 17   | homeserver_config              | buildroot 配置文件                                                |
| 18   | homeserver_kernel_config       | 内核配置文件                                                      |
| 19   | Makefile                       |                                                                   |
| 20   | README.md                      | 当前文档                                                          |
| 21   | sources.list                   | debian 软件源                                                     |
| 22   | VERSION                        | 版本信息                                                          |

## Makefile

| 序号 | 目标                           | 描述                                                              |
|------|--------------------------------|-------------------------------------------------------------------|
| 1    | am335x                         | 编译 am335x 应用程序 (几乎包括所有)                               |
| 2    | am335x-asterisk                | 单独编译 am335x 下的 asterisk                                     |
| 3    | am335x-kernel                  | 编译 am335x 内核                                                  |
| 4    | am335x-kernel-config           | am335x 内核配置                                                   |
| 5    | am335x-nginx                   | 单独编译 am335x 下的 nginx                                        |
| 6    | am335x-php                     | 单独编译 am335x 下的 php                                          |
| 7    | am335x-rootfs                  | 生成 am335x 根文件系统                                            |
| 8    | am335x-sdcard                  | 打包 am335x SD卡程序                                              |
| 9    | am335x-sdcard-install          | 制作 am335x SD卡 (至少1G)                                         |
| 10   | am335x-sdk-install             | 安装 am335x 开发包                                                |
| 11   | am335x-u-boot                  | 编译 am335x u-boot                                                |
| 12   | clean                          | 清理项目 (慎用)                                                   |
| 13   | debian                         | 编译 debian 应用程序 (几乎包括所有)                               |
| 14   | debian-asterisk                | 单独编译 debian 下的 asterisk                                     |
| 15   | debian-nginx                   | 单独编译 debian 下的 nginx                                        |
| 16   | debian-php                     | 单独编译 debian 下的 php                                          |
| 17   | debian-setup                   | debian 安装依赖库                                                 |
| 18   | download                       | 下载依赖文件包                                                    |

## 参考

1. [Linux在线手册](https://www.kernel.org/doc/man-pages)

2. [Asterisk Wiki](https://wiki.asterisk.org)

3. [Nginx官网](http://nginx.org)

4. [Nginx移植(ARM处理器)](http://www.tuicool.com/articles/QZVJjez)

5. [OpenResty最佳实践github地址](https://github.com/moonbingbing/openresty-best-practices)

6. [OpenResty最佳实践-书](https://moonbingbing.gitbooks.io/openresty-best-practices/content/index.html)

7. [w3school](http://www.w3school.com.cn)

8. [菜鸟教程](http://www.runoob.com)

9. [PHP官方手册](http://php.net/manual/zh)

10. [Flight](http://flightphp.com)

11. [Python官方文档2.7](https://docs.python.org/2.7)

12. [Python Package Index](https://pypi.python.org)

13. [Lua5.1官方文档](http://www.lua.org/manual/5.1)

14. [LuaSQLite3](http://lua.sqlite.org)

15. [BitOp](http://bitop.luajit.org)
