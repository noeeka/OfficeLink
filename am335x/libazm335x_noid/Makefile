CC=$(CROSS_COMPILE)gcc
AR=$(CROSS_COMPILE)ar
TOOLCHAINPATH=../arm-eabi-4.4.3/bin
OBJ = libazm335x.o
INCLUDES=-I../u-boot/include 
CFLAGS=-g -Os -fno-common -ffixed-r8 -msoft-float -D__KERNEL__ -ffunction-sections -fdata-sections -fno-builtin -ffreestanding -nostdinc -pipe -DCONFIG_ARM -D__ARM__ -marm -mabi=aapcs-linux -mno-thumb-interwork -march=armv5 -Wall -Wstrict-prototypes -fno-stack-protector -Wno-format-nonliteral -Wno-format-security -isystem $(TOOLCHAINPATH)/../lib/gcc/arm-eabi/4.4.3/include -DCONFIG_SPL_TEXT_BASE=0x402F0400

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS) $(INCLUDES)

libazm335x.lib: $(OBJ)
	$(AR) crv $@ $^

clean:
	$(RM) *.o *.a *.lib

