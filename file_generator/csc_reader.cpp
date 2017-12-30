// Compile with g++ csc_reader.cpp -o csc_reader
// Run with csc_reader <name.stiff/mass>.csc
// Note that this is not a full functioning reader, it only reads and print the first few lines. 

#include <fstream>
#include <stdio.h>

using namespace std;

int main(int argc, char* argv[]) {
	const char* filename = argv[1];
	ifstream fin(filename, ios::binary);
	
	unsigned char label1, label2;
	fin.read((char *)&label1, sizeof(unsigned char));
	fin.read((char *)&label2, sizeof(unsigned char));
	printf("first label is %d\n", label1);
	printf("second label is %d\n", label2);

	int h, w, n;
	fin.read((char *)&h, sizeof(int));
	fin.read((char *)&w, sizeof(int));
	fin.read((char *)&n, sizeof(int));
	printf("height %d, width %d, num of nonzeros %d\n", h, w, n);

	fin.close();
	return 0;

}
