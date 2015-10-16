#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>


#pragma warning(disable: 4996) // Disable deprecation


//See PDF for more details on each variable. https://drive.google.com/a/uci.edu/folderview?id=0B3LD-8zOiOdzfjY3YXJEdGlTZ2Z1ekJGNVlJalpYRmRkOHFFaFI4XzZEaWpFbldLSEt3LW8&usp=sharing
//based on code from: tjohnsen@uci.edu
//encode a spc from XY values

#define MAXHIST 10000
#define TOL 0.01
double xy[MAXHIST];

int main(int argc, char **argv)
{

	if (argc < 3) {
		fprintf(stderr, "use: spcencode <inputfile.txt> <outputfile.spc | \"-\" (stdout)> [x-axis nbr 0..255,default 13] [y-axis nbr 0..255, def. 4] [expermiment code 0..15, default 10] [\"memo ... \" cutoff 159 chars]\n");
		return 1;
	}

	FILE *fout = stdout;
	if (argv[2][0]!='-') fout=fopen(argv[2], "wb+"); 
	if (!fout) {
		fprintf(stderr, "Unable to open file %s!", argv[1]);
		return 1;
	}
	FILE *fin = fopen(argv[1], "rb"); 
	if (!fin) {
		fprintf(stderr, "Unable to open file %s !", argv[2]);
		return 1;
	}
	unsigned xa = 13, ya = 4,expr=10;
	char memo[200];
	if (argc>3) { xa = (unsigned)atoi(argv[3]); }
	if (argc>4) { ya = (unsigned)atoi(argv[4]); }
	if (argc>5) { expr = (unsigned)atoi(argv[5]); }
	if (argc > 6) { memset(memo, 0x00, sizeof(memo));  strncpy(memo, argv[6], 159); }


	// variables used to store different mem sizes
	int i = 0;              // int, 4 bytes
	unsigned char b = 'a';  // byte, 1 byte
	double d = 0;           // double, 8 bytes
	float f = 0;            // float, 4 bytes
	short int w = 0;        // word, 2 bytes

							// variables we actually need
	int power2 = 0; // we use this to multiply to the y value (integer data value representing intensity) later
	int numDataPoints = 0; // used to divide first and last x coord, for increments in x values (wavenumbers)
	double firstXCoord = 0; // first logged x value (wavenumber)
	double lastXCoord = 0; // last logged x value (Wavenumber
	int numSubFiles = 1;

	char s[256], *sp = 0;
	double x = 0, y = 0, interval = 0;
	int it = 0;
	while (fgets(s, 256, fin) && it<MAXHIST) {
		sp = strtok(s, "\t");
		if (sp && *sp >= '0' && *sp <= '9') x = atof(sp); else continue;  //x values should be positive and fixed interval 
		sp = strtok(NULL, "\t");
		if (sp) y = atof(sp); else continue;

		xy[it++] = y;
		if (1 == it) {
			firstXCoord = x; lastXCoord = x; continue;
		}
		if (2 == it) interval = fabs(firstXCoord - x);
		else {
			double v = fabs(x - lastXCoord);
			if (fabs(interval - v) > TOL || interval < TOL) { fprintf(stderr, "unequal spaced xy data (interval should be %g and was %g-%g)\n", interval, lastXCoord, x); return 2; }
		}
		lastXCoord = x;
	}
	if (it == MAXHIST) {
		fprintf(stderr, "too many values"); return 2;
	}
	numDataPoints = it;


	// main header
	b = 0x00;  fwrite(&b, sizeof(b), 1, fout); // flags represent different things (see pdf)
	b = 0x4b;  fwrite(&b, sizeof(b), 1, fout); // spc file version
	b = expr;  fwrite(&b, sizeof(b), 1, fout); // experiment type code
	b = 0x80;  fwrite(&b, sizeof(b), 1, fout); // IMPORTANT exponenet for Y values
	power2 = (int)b; // save our exponent for multiplying
	i = numDataPoints;  fwrite(&i, sizeof(i), 1, fout); // IMPORTANT number of points in file	
	d = firstXCoord;  fwrite(&d, sizeof(d), 1, fout); // IMPORTANT first x coordinate	
	d = lastXCoord;  fwrite(&d, sizeof(d), 1, fout); // IMPORTANT last x coordinate	
	i = numSubFiles = 1;  fwrite(&i, sizeof(i), 1, fout); // IMPORTANT Number of subfiles
	b = xa;  fwrite(&b, sizeof(b), 1, fout); // X units type code
	b = ya;  fwrite(&b, sizeof(b), 1, fout); // Y units type code
	b = 0x00;  fwrite(&b, sizeof(b), 1, fout); // Z units type code
	b = 0x00;  fwrite(&b, sizeof(b), 1, fout); // Posting disposition
	i = 2107759074; fwrite(&i, sizeof(i), 1, fout); // compressed date (see pdf for format)
	b = 0x00;  for (unsigned int j = 0; j < 9; j++) // resolution description text
		fwrite(&b, sizeof(b), 1, fout);
	b = 0x00; for (unsigned int j = 0; j < 9; j++) // source instrument description text
		fwrite(&b, sizeof(b), 1, fout);
	w = 0;  fwrite(&w, sizeof(w), 1, fout); // peak point number for interferograms
	f = 0;  for (unsigned int j = 0; j < 8; j++) // spare
		fwrite(&f, sizeof(f), 1, fout);
	b = 0;  for (unsigned int j = 0; j < 130; j++) // Memo
		fwrite( (const void*)( memo +j), sizeof(b), 1, fout);
	b = 0;  for (unsigned int j = 0; j < 30; j++)  // x, y, and z custom axis strings (combined)
		fwrite((const void*)(memo + j+130), sizeof(b), 1, fout);
	i = 0;   fwrite(&i, sizeof(i), 1, fout); // byte offset to log block
	i = 0; fwrite(&i, sizeof(i), 1, fout); // file modification flag
	b = 0; fwrite(&b, sizeof(b), 1, fout); // processing code
	b = 0; fwrite(&b, sizeof(b), 1, fout); // calibration level + 1
	w = 0; fwrite(&w, sizeof(w), 1, fout); // sub method sample injection number
	f = 0; fwrite(&f, sizeof(f), 1, fout); // floatind data multiplier concentration factor
	b = 0;  for (unsigned int j = 0; j < 48; j++)  // method file
		fwrite(&b, sizeof(b), 1, fout);
	f = 0; fwrite(&f, sizeof(f), 1, fout); // Z subfile increment for even Z multifiles
	i = 0; fwrite(&i, sizeof(i), 1, fout); // number of w planes
	f = 0;  fwrite(&f, sizeof(f), 1, fout); // w plane increment
	b = 0;  fwrite(&b, sizeof(b), 1, fout); // w axis units code
	b = 0;  for (unsigned int j = 0; j < 187; j++) // reserved
		fwrite(&b, sizeof(b), 1, fout);
	// end main header

	// do this for all subfiles
	for (unsigned int subFile = 0; subFile < numSubFiles; subFile++) {
		// start sub folder for file (Even if only one file here)
		b = 0x00;  fwrite(&b, sizeof(b), 1, fout); // subfiles flags (See pdf)
		b = 0x80;  fwrite(&b, sizeof(b), 1, fout); // exponenet for sufiles y values
		if ((int)b != 0) // my files at least had this area blank sinc had only one sub file
			power2 = (int)b; // multiple sub files may have his changed, make sure to check other values for similar things
		w = 0;  fwrite(&w, sizeof(w), 1, fout); // subfile index number
		f = 0.0; fwrite(&f, sizeof(f), 1, fout); // subfiels starting z value
		f = 0.0; fwrite(&f, sizeof(f), 1, fout); // subfiles ending z value
		f = 0.0; fwrite(&f, sizeof(f), 1, fout); // subfiles noise value to use peak picking
		i = 0.0; fwrite(&i, sizeof(i), 1, fout); // number of points if XYXY multifile
		i = 0.0; fwrite(&i, sizeof(i), 1, fout); // number of co-added scans
		f = 0.0; fwrite(&f, sizeof(f), 1, fout); // w axis value
		b = 0x00;  for (unsigned int j = 0; j < 4; j++) // reserved
			fwrite(&b, sizeof(b), 1, fout);


		// start data entry for only x values
		for (unsigned int j = 0; j < numDataPoints; j++) {
			f = (float)xy[j];  fwrite(&f, sizeof(i), 1, fout); // read in data value
		}
		// end data for x values
	}

	fclose(fout);
	return 0;
}

