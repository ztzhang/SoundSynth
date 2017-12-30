// Compile with g++ vmap_generator.cpp -o vmap_generator
// Run with vmap_generator <name>.geo.txt <name>.vmap
// Assuming there is no fixed vertices. 

#include <fstream>
#include <stdio.h>

using namespace std;

int main(int argc, char* argv[]) {
    const char* filename = argv[1];
    const char* outfilename = argv[2];

    ifstream fin(filename, ios::in);
    FILE * outFile;
    outFile = fopen(outfilename, "w");

    int nsv;
    int nfv = 0;
    fin >> nsv;
    fin.ignore();
    fprintf(outFile, "%d %d\n", nfv, nsv);

    while (fin.good()){
        int tet_id, tgl_id;
        double x, y, z, a;
        
        fin >> tet_id >> tgl_id >> x >> y >> z >> a;
        fin.ignore();
        if (fin.eof()) break;
        fprintf(outFile, "%d %d\n", tet_id, tgl_id);
    }

    fin.close();
    fclose(outFile);

    return 0;
}
