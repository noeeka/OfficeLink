#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <stdlib.h>
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

enum {
    SUCCESS,
    ERROR,
};

/* 设置串口参数 */
static int uart_ctl(int fd, int baudrate, int bytesize, char parity, int stopbits) {
    struct termios tios, old_tios;
    speed_t speed;

    /* Save */
    tcgetattr(fd, &old_tios);

    memset(&tios, 0, sizeof(struct termios));

    /* C_ISPEED     Input baud (new interface)
     C_OSPEED     Output baud (new interface)
     */
    switch (baudrate) {
    case 110:
        speed = B110;
        break;
    case 300:
        speed = B300;
        break;
    case 600:
        speed = B600;
        break;
    case 1200:
        speed = B1200;
        break;
    case 2400:
        speed = B2400;
        break;
    case 4800:
        speed = B4800;
        break;
    case 9600:
        speed = B9600;
        break;
    case 19200:
        speed = B19200;
        break;
    case 38400:
        speed = B38400;
        break;
    case 57600:
        speed = B57600;
        break;
    case 115200:
        speed = B115200;
        break;
    default:
        speed = B9600;
        // log_warning("WARNING Unknown baud rate");
        printf("WARNING Unknown baud rate\n");
    }

    /* Set the baud rate */
    if ((cfsetispeed(&tios, speed) < 0) || (cfsetospeed(&tios, speed) < 0)) {
        return ERROR;
    }

    /* C_CFLAG      Control options
     CLOCAL       Local line - do not change "owner" of port
     CREAD        Enable receiver
     */
    tios.c_cflag |= (CREAD | CLOCAL);
    /* CSIZE, HUPCL, CRTSCTS (hardware flow control) */

    /* Set data bits (5, 6, 7, 8 bits)
     CSIZE        Bit mask for data bits
     */
    tios.c_cflag &= ~CSIZE;
    switch (bytesize) {
    case 5:
        tios.c_cflag |= CS5;
        break;
    case 6:
        tios.c_cflag |= CS6;
        break;
    case 7:
        tios.c_cflag |= CS7;
        break;
    case 8:
    default:
        tios.c_cflag |= CS8;
        break;
    }

    /* Stop bit (1 or 2) */
    if (stopbits == 1)
        tios.c_cflag &= ~ CSTOPB;
    else
        /* 2 */
        tios.c_cflag |= CSTOPB;

    /* PARENB       Enable parity bit
     PARODD       Use odd parity instead of even */
    if (parity == 'N') {
        /* None */
        tios.c_cflag &= ~ PARENB;
    } else if (parity == 'E') {
        /* Even */
        tios.c_cflag |= PARENB;
        tios.c_cflag &= ~ PARODD;
    } else {
        /* Odd */
        tios.c_cflag |= PARENB;
        tios.c_cflag |= PARODD;
    }

    /* Read the man page of termios if you need more information. */

    /* This field isn't used on POSIX systems
     tios.c_line = 0;
     */

    /* C_LFLAG      Line options

     ISIG Enable SIGINTR, SIGSUSP, SIGDSUSP, and SIGQUIT signals
     ICANON       Enable canonical input (else raw)
     XCASE        Map uppercase \lowercase (obsolete)
     ECHO Enable echoing of input characters
     ECHOE        Echo erase character as BS-SP-BS
     ECHOK        Echo NL after kill character
     ECHONL       Echo NL
     NOFLSH       Disable flushing of input buffers after
     interrupt or quit characters
     IEXTEN       Enable extended functions
     ECHOCTL      Echo control characters as ^char and delete as ~?
     ECHOPRT      Echo erased character as character erased
     ECHOKE       BS-SP-BS entire line on line kill
     FLUSHO       Output being flushed
     PENDIN       Retype pending input at next read or input char
     TOSTOP       Send SIGTTOU for background output

     Canonical input is line-oriented. Input characters are put
     into a buffer which can be edited interactively by the user
     until a CR (carriage return) or LF (line feed) character is
     received.

     Raw input is unprocessed. Input characters are passed
     through exactly as they are received, when they are
     received. Generally you'll deselect the ICANON, ECHO,
     ECHOE, and ISIG options when using raw input
     */

    /* Raw input */
    tios.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);

    /* C_IFLAG      Input options

     Constant     Description
     INPCK        Enable parity check
     IGNPAR       Ignore parity errors
     PARMRK       Mark parity errors
     ISTRIP       Strip parity bits
     IXON Enable software flow control (outgoing)
     IXOFF        Enable software flow control (incoming)
     IXANY        Allow any character to start flow again
     IGNBRK       Ignore break condition
     BRKINT       Send a SIGINT when a break condition is detected
     INLCR        Map NL to CR
     IGNCR        Ignore CR
     ICRNL        Map CR to NL
     IUCLC        Map uppercase to lowercase
     IMAXBEL      Echo BEL on input line too long
     */
    if (parity == 'N') {
        /* None */
        tios.c_iflag &= ~INPCK;
    } else {
        tios.c_iflag |= INPCK;
    }

    /* Software flow control is disabled */
    tios.c_iflag &= ~(IXON | IXOFF | IXANY);

    /* C_OFLAG      Output options
     OPOST        Postprocess output (not set = raw output)
     ONLCR        Map NL to CR-NL

     ONCLR ant others needs OPOST to be enabled
     */

    /* Raw ouput */
    tios.c_oflag &= ~ OPOST;

    /* C_CC         Control characters
     VMIN         Minimum number of characters to read
     VTIME        Time to wait for data (tenths of seconds)

     UNIX serial interface drivers provide the ability to
     specify character and packet timeouts. Two elements of the
     c_cc array are used for timeouts: VMIN and VTIME. Timeouts
     are ignored in canonical input mode or when the NDELAY
     option is set on the file via open or fcntl.

     VMIN specifies the minimum number of characters to read. If
     it is set to 0, then the VTIME value specifies the time to
     wait for every character read. Note that this does not mean
     that a read call for N bytes will wait for N characters to
     come in. Rather, the timeout will apply to the first
     character and the read call will return the number of
     characters immediately available (up to the number you
     request).

     If VMIN is non-zero, VTIME specifies the time to wait for
     the first character read. If a character is read within the
     time given, any read will block (wait) until all VMIN
     characters are read. That is, once the first character is
     read, the serial interface driver expects to receive an
     entire packet of characters (VMIN bytes total). If no
     character is read within the time allowed, then the call to
     read returns 0. This method allows you to tell the serial
     driver you need exactly N bytes and any read call will
     return 0 or N bytes. However, the timeout only applies to
     the first character read, so if for some reason the driver
     misses one character inside the N byte packet then the read
     call could block forever waiting for additional input
     characters.

     VTIME specifies the amount of time to wait for incoming
     characters in tenths of seconds. If VTIME is set to 0 (the
     default), reads will block (wait) indefinitely unless the
     NDELAY option is set on the port with open or fcntl.
     */
    /* Unused because we use open with the NDELAY option */
    tios.c_cc[VMIN] = 0;
    tios.c_cc[VTIME] = 0;

    if (tcsetattr(fd, TCSANOW, &tios) < 0) {
        return ERROR;
    }
    return SUCCESS;
}

static int uart_set(lua_State *L) {
    int fd = luaL_checkinteger(L, 1);
    int baudrate = luaL_checkinteger(L, 2);
    int bytesize = luaL_checkinteger(L, 3);
    char parity = luaL_checkinteger(L, 4);
    int stopbits = luaL_checkinteger(L, 5);
    lua_pushinteger(L, uart_ctl(fd, baudrate, bytesize, parity, stopbits));
    return 1;
}

static const luaL_Reg uart_lib[] = {
  {"ctl"      , uart_set},
  {NULL, NULL}
};

LUALIB_API int luaopen_luart(lua_State *L) {
  luaL_register(L, "luart", uart_lib);
  return 1;
}
