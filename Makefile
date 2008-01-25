E = @echo
Q = @
MANPAGEDIR=/usr/local/share/man/man1

all:
	$(E) "  * Building Mother...." 
	$(Q) python setup.py build

install:
	$(E) "  * Installing Mother ...." 
	$(Q) python setup.py install
	$(E) "  * Installing mothermapper manpage on ${MANPAGEDIR} ...." 
	$(Q) mkdir -p ${MANPAGEDIR}
	$(Q) cp doc/mothermapper.1 ${MANPAGEDIR}

