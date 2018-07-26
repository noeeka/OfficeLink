#############################################################
#
# jansson
#
#############################################################

JANSSON_VERSION = 2.7
JANSSON_SITE = http://www.digip.org/jansson/releases
JANSSON_INSTALL_STAGING = YES

$(eval $(autotools-package))
