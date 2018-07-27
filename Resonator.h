#include<cstddef>
#include<math.h>

class Resonator{	
	private:
		float w;
		float r;
		int b0;
		int b1;
		int b2;
		float a1;
		float a2;
		float buffer1;
		float buffer2;
		float x;		
       	public:
		Resonator(float f,float q,int SAMPLE_RATE);
		float filter();
};
