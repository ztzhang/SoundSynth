%% solving Helmholtz:
function BEMsolver(cur_dir,overwrite)
root = cur_dir;
prefix=[];
addpath('/data/vision/billf/object-properties/sound/software/nihu/src/bin/matlab');
addpath('/data/vision/billf/object-properties/sound/software/nihu/src/bin/tutorial');
run install.m
%%
mesh=[];
load([root,'/bem_input/mesh.mat']);
load([root,'/bem_input',prefix,'/init_bem.mat']);
load([root,'/bem_input',prefix,'/freq.mat']);
%
face = [32303*ones(size(mesh.face,1),1),double(mesh.face)-1];

%[cent,nrm] = ctn(r_nodes,r_elem)

for mode = 1:length(freq)
system(['bash /data/vision/billf/object-properties/sound/ztzhang/renew/re_new.sh']);
name = sprintf('output-%d.dat',mode-1);
mode
%if exist([root,'/bem_result',prefix,'/',name],'file') && overwrite==0
%	fprintf('SKIP!!!!')
 %   continue
%end
freq_cur= freq(mode);
%// call C++ code for Matrix construction.
fprintf('preparing matrix for mode %d(freq %4.3f): \n',mode,freq(mode));
tic
k = 2*pi*freq_cur/343;
[Ls, Ms, Lf, Mf] = helmholtz_bem_3d(mesh.vertex,face, [], [], k);
toc
rho = 1.184;
qs_fbem = init_bem(mode,:);
qs_ana = conj(qs_fbem.*(1i*2*pi*freq_cur*rho))*-1;
fprintf('calculating Initial pressure for mode %d(freq %4.3f): \n',mode,freq(mode));
tic
ps_num = Ms \ (Ls * qs_ana.');
toc
name = sprintf('output-%d.dat',mode-1);
fileID = fopen([root,'/bem_result',prefix,'/',name],'w+');
fprintf(fileID, '  Freq. No. =   1,  f = %1.4s (Hz),  k = (0.1832D+01, 0.0000D+00):\n',freq(mode));
fprintf(fileID, ' Solution on the Boundary:\n');
fprintf(fileID, 'Elements: this line is just for fun \n');
for k = 1:length(ps_num)
    fprintf(fileID,sprintf('%d ( %1.6s , %1.6s ) \n',k,real(ps_num(k)),-imag(ps_num(k))));
end
fclose(fileID);
end