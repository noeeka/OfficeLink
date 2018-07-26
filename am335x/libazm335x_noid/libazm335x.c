
#include <common.h>
#include <asm/cache.h>
#include <asm/omap_common.h>
#include <asm/io.h>
#include <asm/arch/cpu.h>
#include <asm/arch/ddr_defs.h>
#include <asm/arch/hardware.h>
#include <asm/arch/mmc_host_def.h>
#include <asm/arch/sys_proto.h>
#include <asm/arch/mem.h>
#include <asm/arch/nand.h>
#include <asm/arch/clock.h>
#include <linux/mtd/nand.h>
#include <nand.h>
#include <net.h>
#include <miiphy.h>
#include <netdev.h>
#include <spi_flash.h>
#include "tps65217.h"
#include <i2c.h>
#include <serial.h>

/**
 * tps65217_reg_read() - Generic function that can read a TPS65217 register
 * @src_reg:          Source register address
 * @src_val:          Address of destination variable
 */

static unsigned char tps65217_reg_read(uchar src_reg, uchar *src_val)
{
	if (i2c_read(TPS65217_CHIP_PM, src_reg, 1, src_val, 1))
		return 1;
	return 0;
}

/**
 *  tps65217_reg_write() - Generic function that can write a TPS65217 PMIC
 *                         register or bit field regardless of protection
 *                         level.
 *
 *  @prot_level:        Register password protection.
 *                      use PROT_LEVEL_NONE, PROT_LEVEL_1, or PROT_LEVEL_2
 *  @dest_reg:          Register address to write.
 *  @dest_val:          Value to write.
 *  @mask:              Bit mask (8 bits) to be applied.  Function will only
 *                      change bits that are set in the bit mask.
 *
 *  @return:            0 for success, 1 for failure.
 */
static int tps65217_reg_write(uchar prot_level, uchar dest_reg,
        uchar dest_val, uchar mask)
{
        uchar read_val;
        uchar xor_reg;

        /* if we are affecting only a bit field, read dest_reg and apply the mask */
        if (mask != MASK_ALL_BITS) {
                if (i2c_read(TPS65217_CHIP_PM, dest_reg, 1, &read_val, 1))
                        return 1;
                read_val &= (~mask);
                read_val |= (dest_val & mask);
                dest_val = read_val;
        }

        if (prot_level > 0) {
                xor_reg = dest_reg ^ PASSWORD_UNLOCK;
                if (i2c_write(TPS65217_CHIP_PM, PASSWORD, 1, &xor_reg, 1))
                        return 1;
        }

        if (i2c_write(TPS65217_CHIP_PM, dest_reg, 1, &dest_val, 1))
                return 1;

        if (prot_level == PROT_LEVEL_2) {
                if (i2c_write(TPS65217_CHIP_PM, PASSWORD, 1, &xor_reg, 1))
                        return 1;

                if (i2c_write(TPS65217_CHIP_PM, dest_reg, 1, &dest_val, 1))
                        return 1;
        }

        return 0;
}

/**
 *  tps65217_voltage_update() - Controls output voltage setting for the DCDC1,
 *       DCDC2, or DCDC3 control registers in the PMIC.
 *
 *  @dc_cntrl_reg:      DCDC Control Register address.
 *                      Must be DEFDCDC1, DEFDCDC2, or DEFDCDC3.
 *  @volt_sel:          Register value to set.  See PMIC TRM for value set.
 *
 *  @return:            0 for success, 1 for failure.
 */
static int tps65217_voltage_update(unsigned char dc_cntrl_reg, unsigned char volt_sel)
{
        if ((dc_cntrl_reg != DEFDCDC1) && (dc_cntrl_reg != DEFDCDC2)
                && (dc_cntrl_reg != DEFDCDC3))
                return 1;

        /* set voltage level */
        if (tps65217_reg_write(PROT_LEVEL_2, dc_cntrl_reg, volt_sel, MASK_ALL_BITS))
                return 1;

        /* set GO bit to initiate voltage transition */
        if (tps65217_reg_write(PROT_LEVEL_2, DEFSLEW, DCDC_GO, DCDC_GO))
                return 1;

        return 0;
}

int check_azm335x_serialno(void)
{
    unsigned long *pserialout = (unsigned long*) (CONFIG_SPL_TEXT_BASE);
    
    pserialout[0] = 0x6c6c6920;
    pserialout[1] = 0x6c616765;
    return 1;
}

int azm335x_board_init(void)
{
	uchar pmic_status_reg;

    if (tps65217_reg_read(STATUS, &pmic_status_reg))
    {
        printf("check tps65217 failure\n");
        return -1;
    }
    check_azm335x_serialno();
#if 0
    /* Increase USB current limit to 1300mA */
    if (tps65217_reg_write(PROT_LEVEL_NONE, POWER_PATH,
                USB_INPUT_CUR_LIMIT_1300MA,
                USB_INPUT_CUR_LIMIT_MASK))
        printf("tps65217_reg_write failure\n");
#else
    /* disable USB Power */
    if (tps65217_reg_write(PROT_LEVEL_NONE, POWER_PATH,
                0x00,
                0x10))
        printf("tps65217_reg_write failure\n");
#endif        
    /* Set DCDC2 (MPU) voltage to 1.275V */
    if (tps65217_voltage_update(DEFDCDC2,
                DCDC_VOLT_SEL_1275MV)) {
        printf("tps65217_voltage_update failure\n");
        return -1;
    }
    //printf("Set DCDC2 (MPU) voltage to 1.275\n");

    /* Set LDO3, LDO4 output voltage to 3.3V */
    if (tps65217_reg_write(PROT_LEVEL_2, DEFLS1,
                LDO_VOLTAGE_OUT_3_3, LDO_MASK))
        printf("tps65217_reg_write failure\n");

    if (tps65217_reg_write(PROT_LEVEL_2, DEFLS2,
                LDO_VOLTAGE_OUT_3_3, LDO_MASK))
        printf("tps65217_reg_write failure\n");

    //printf("Set LDO3, LDO4 output voltage to 3.3V\n");
    if (!(pmic_status_reg & PWR_SRC_AC_BITMASK)) {
        printf("No AC power, disabling frequency switch\n");
        return -1;
    }
    return 0;
}

