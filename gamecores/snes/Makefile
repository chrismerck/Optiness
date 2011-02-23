
snes.so: snes.pyx
	python2 setup.py build_ext --inplace

all: snes.so

clean:
	rm -f snes.cpp
	rm -rf build/

fclean: clean
	rm -f snes.so

