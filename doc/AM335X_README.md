# 笔记

* AM335x u-boot参数 (uEnv.txt)

    ```
    loadbootargs=setenv bootargs 'console=ttyO0,115200n8 mem=128M root=/dev/ram ip=off'
    loadbootcmd=setenv bootcmd 'nand read 0x80007fc0 0x100000 0x400000;bootm 0x80007fc0 0x82000000'
    savebootargs=setenv bootargs 'console=ttyO0,115200n8 noinitrd mem=128M ip=off rootwait=1 rw ubi.mtd=5,2048 rootfstype=ubifs root=ubi0:rootfs'
    savebootcmd=setenv bootcmd 'nand read 0x80007fc0 0x100000 0x400000;bootm 0x80007fc0';saveenv
    restoreboot=nand scrub.chip;mmc rescan;fatload mmc 0 0x80100000 MLON;nand write 0x80100000 0 0x10000;fatload mmc 0 0x80100000 u-bootn.img;nand write 0x80100000 0x80000 0x40000
    restorekernel=fatload mmc 0 0x80100000 uImage;nand write 0x80100000 0x100000 0x400000
    loadramdisk=fatload mmc 0 0x82000000 rootfs.ext2.gz.img;
    uenvcmd=run restoreboot;run restorekernel;run loadramdisk;run savebootargs;run savebootcmd;run loadbootcmd;run loadbootargs;boot
    ```

* AM335x Flash烧写

    ```
    nand scrub.chip;mmc rescan;fatload mmc 0 0x80100000 MLON;nand write 0x80100000 0 0x10000;fatload mmc 0 0x80100000 u-bootn.img;nand write 0x80100000 0x80000 0x40000
    fatload mmc 0 0x80100000 uImage;nand write 0x80100000 0x100000 0x400000
    fatload mmc 0 0x82000000 rootfs.ext2.gz.img
    savebootargs=setenv bootargs 'console=ttyO0,115200n8 noinitrd mem=128M ip=off rootwait=1 rw ubi.mtd=5,2048 rootfstype=ubifs root=ubi0:rootfs'
    setenv bootcmd 'nand read 0x80007fc0 0x100000 0x400000;bootm 0x80007fc0';saveenv
    setenv bootcmd 'nand read 0x80007fc0 0x100000 0x400000;bootm 0x80007fc0 0x82000000'
    setenv bootargs 'console=ttyO0,115200n8 mem=128M root=/dev/ram ip=off'
    boot
    ```

* AM335x Flash分布

    ```
    0x000000000000-0x000000020000 : "SPL"
    0x000000020000-0x000000080000 : "U-Boot Env"
    0x000000080000-0x000000100000 : "U-Boot"
    0x000000100000-0x000000500000 : "Kernel"
    0x000000500000-0x000001000000 : "RAMDISK"
    0x000001000000-0x000040000000 : "File System"
    ```

* AM335x 烧写内核、文件系统

    ```
    mmc rescan;nand scrub 100000 400000
    fatload mmc 0 0x80100000 uImage;nand write 0x80100000 0x100000 0x400000
    mmc rescan;nand scrub 1000000 3F000000;fatload mmc 0 0x82000000 rootfs.ext2.gz.img
    setenv bootcmd 'nand read 0x80007fc0 0x100000 0x400000;bootm 0x80007fc0 0x82000000'
    setenv bootargs 'console=ttyO0,115200n8 mem=128M root=/dev/ram ip=off'
    boot
    ```

* AM335x tftp 烧写内核

    ```
    setenv ipaddr 192.168.1.159
    setenv serverip 192.168.1.8
    tftpboot uImage
    nand scrub 100000 400000;nand write 0x82000000 0x100000 0x400000
    ```

* AM335x tftp 烧写u-boot

    ```
    setenv ipaddr 192.168.1.159
    setenv serverip 192.168.1.158
    tftpboot u-boot.bin
    nand scrub 0x80000 0x40000;nand write 0x82000000 0x80000 0x40000
    ```

* Debian 安装无线网卡驱动

    ```
    apt-get update && apt-get install firmware-brcm80211
    ```

* Debian 32位环境

    ```
    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install lib32z1 lib32ncurses5
    sudo apt-get install lib32c++
    ```

* Linux 静态IP设置

    ```
    auto eth0
    iface eth0 inet static
    address 192.168.1.156
    gateway 192.168.1.1
    netmask 255.255.255.0
    network 192.168.1.1
    broadcast 192.168.1.255
    ```
