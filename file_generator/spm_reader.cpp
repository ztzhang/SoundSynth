// Compile with g++ spm_reader.cpp -o spm_reader
// Run with spm_reader <name.stiff/mass>.spm <name.stiff/mass>.dat

#include <fstream>
#include <stdio.h>

using namespace std;

int main(int argc, char* argv[]) {
	const char* filename = argv[1];
	const char* outfilename = argv[2];

	ifstream fin(filename, ios::binary);	
	FILE * pFile;
	pFile = fopen(outfilename, "w");

	unsigned char label;
	fin.read((char *)&label, sizeof(unsigned char));
	printf("first label is %d\n", label);

	int h, w, n;
	fin.read((char *)&h, sizeof(int));
	fin.read((char *)&w, sizeof(int));
	fin.read((char *)&n, sizeof(int));
	printf("height %d, width %d, num of nonzeros %d\n", h, w, n);

	for (int i = 0; i < n; i++) {
		int row, col;
		double val;
		fin.read((char *)&row, sizeof(int));
		fin.read((char *)&col, sizeof(int));
		fin.read((char *)&val, sizeof(double));
		fprintf(pFile, "%d %d %.15f\n", row, col, val);
	}
	
	fprintf(pFile, "%d %d %.15f\n", h, w, 0.0);

	fin.close();
	fclose(pFile);

	return 0;
}
