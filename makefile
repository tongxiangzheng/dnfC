prefix = /usr
all:
	
clean:

distclean: clean

build:
	-pip3 install wget rarfile spdx-tools cyclonedx-bom cyclonedx-python-lib winrar --target ./src/lib

install:
	mkdir -p $(DESTDIR)$(prefix)/bin
	cp bin/* $(DESTDIR)$(prefix)/bin/
	mkdir -p $(DESTDIR)$(prefix)/share/dnfC
	cp -r src/* $(DESTDIR)$(prefix)/share/dnfC/

uninstall:
	-rm -f $(DESTDIR)$(prefix)/bin/dnfc
	-rm -rf $(DESTDIR)$(prefix)/share/dnfC

.PHONY: all install clean distclean uninstall
