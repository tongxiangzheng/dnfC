prefix = /usr
all:
	
clean:

distclean: clean

install:
	mkdir -p $(DESTDIR)$(prefix)/bin
	cp bin/* $(DESTDIR)$(prefix)/bin/
	mkdir -p $(DESTDIR)$(prefix)/share/dnfC
	cp -r src/* $(DESTDIR)$(prefix)/share/dnfC/

uninstall:
	-rm -f $(DESTDIR)$(prefix)/bin/yumc
	-rm -f $(DESTDIR)$(prefix)/bin/dnfc

.PHONY: all install clean distclean uninstall
