prefix = /usr
all:
	
clean:

distclean: clean

build:
	-pip3 install wget rarfile spdx-tools cyclonedx-bom cyclonedx-python-lib winrar --target ./src/lib

install:
	mkdir -p $(DESTDIR)/usr/sbin
	cp bin/* $(DESTDIR)/usr/sbin/
	mkdir -p $(DESTDIR)/usr/share/dnfC
	cp -r src/* $(DESTDIR)/usr/share/dnfC/
	mkdir -p $(DESTDIR)/etc/
	cp -r src/* $(DESTDIR)/etc/

uninstall:
	-rm -f $(DESTDIR)/usr/sbin/dnfc
	-rm -rf $(DESTDIR)/usr/share/dnfC

.PHONY: all install clean distclean uninstall
