/*
   touch key drivers  add by yonhan at 2015.11.18   
   first version from wangsu edited by yonhan 
*/
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/gpio.h>
#include <linux/platform_device.h>
#include <linux/delay.h>
#include <linux/interrupt.h>
#include <linux/suspend.h>
#include <asm/uaccess.h>
#define DEVICE_NAME         "led-work"
static int rc;

void __iomem *base;
static struct cdev cdev_led;
static dev_t dev_number;
static struct class *dev_class;

static int dev_open(struct inode *inode, struct file *filp)
{
    return 0;
}

static int dev_release(struct inode *inode, struct file *filp){
    return 0;
}

static ssize_t fops_write(struct file *file, const char __user *buf, size_t len, loff_t *off) {
    char data;
    if(copy_from_user(&data, buf, sizeof(char))) {
        return -EFAULT;
    }
    if('1' == data) {
        __raw_writel(4, base+0x820);
    } else {
        __raw_writel(7, base+0x820);
    }
    return sizeof(char);
}

static struct file_operations dev_fops = {
    .owner = THIS_MODULE,
    .open = dev_open,
    .release = dev_release,
    .write   = fops_write,
};
static int dev_init(void)
{
    base = ioremap(0x44E10000LU, SZ_4K);
    if (WARN_ON(!base))
        return -ENOMEM;
    if(alloc_chrdev_region(&dev_number, 0, 1, DEVICE_NAME)) {
        printk(KERN_DEBUG "alloc_chrdev_region fail\n");
    }
    cdev_init(&cdev_led, &dev_fops);
    cdev_led.owner = THIS_MODULE;
    rc = cdev_add(&cdev_led, dev_number, 1);
    if(rc) {
        printk(KERN_DEBUG "cdev_add fail\n");
        return rc;
    }
    dev_class = class_create(THIS_MODULE, DEVICE_NAME);
    device_create(dev_class, NULL, dev_number, NULL, DEVICE_NAME);

    printk(KERN_DEBUG "dev_init success\n");
    return 0;
}
static void dev_exit(void)
{
    unregister_chrdev_region(dev_number, 1);
    device_destroy(dev_class, dev_number);
    cdev_del(&cdev_led);
    class_destroy(dev_class);
    iounmap(base);
}
module_init(dev_init);
module_exit(dev_exit);
