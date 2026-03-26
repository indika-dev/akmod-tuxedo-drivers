all: rpm
	
rpm:
	spectool -g ${PWD}/tuxedo-drivers.spec
	fedpkg --release f43 mockbuild --enable-network

build:
	sudo akmods --akmod tuxedo-drivers

lint:
	rpm -q --specfile tuxedo-drivers.spec

clean:
	rm -rf tmp
	rm -rf results_*
	rm -f *.src.rpm
	rm -f *.tar.gz
	rm -f results_tuxedo-drivers
