### Instructions to generate .ev and .vmap files###

1. Run `./vmap_generator <name>.geo.txt <name>.vmap`
2. Run `./spm_reader <name>.stiff.spm <name>.stiff.dat`
3. Run `./spm_reader <name>.mass.spm <name>.mass.dat`
4. Run `matlab -nodisplay -nodesktop`

	```>> ev_generator('<name>.stiff.dat', '<name>.mass.dat', fmin, fmax, density, '<name>.ev')```
