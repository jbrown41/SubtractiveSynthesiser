INC=../include
SOURCE=../src/*.c

all: Resonator.py _Resonator.so

Resonator.py: Resonator.i
	swig -c++ -python Resonator.i

_Resonator.so: Resonator.o Resonator_wrap.o
	g++ -shared Resonator.o Resonator_wrap.o -o _Resonator.so

Resonator.o: Resonator.cxx
	g++ -fPIC -c Resonator.cxx 

Resonator_wrap.o: Resonator_wrap.cxx
	g++ -fPIC -c Resonator_wrap.cxx $$(python3-config --includes --ldflags)

Resonator_wrap.cxx: Resonator.py

clean:
	rm *o Resonator.py Resonator_wrap.cxx
