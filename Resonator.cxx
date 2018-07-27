#include <cstddef>
#include <cmath>
#include "Resonator.h"

Resonator::Resonator(float f, float q, int SAMPLE_RATE) :
	w(2*atan(1)*4*(f/SAMPLE_RATE)),r{1-sin(w/q)},b0{1},b1{0}
	,b2{0},a1{-2*r*cos(w)},a2(pow(r,2)),buffer1{0},buffer2{0},x{f}
{
}

float Resonator::filter(){
		float v=static_cast <float> (rand())/static_cast <float> (RAND_MAX);

		float acc_input=v-buffer1*a1-buffer2*a2;
		

		
		buffer2=buffer1;
		buffer1=acc_input;
		return acc_input;
		//return acc_output;
}
