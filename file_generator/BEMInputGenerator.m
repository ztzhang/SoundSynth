function BEMInputGenerator(currentdir, name, density, alpha, beta,overwrite)
root = currentdir;
fprintf(root);
%% Read .ev file
filePath = [root,'/',name,'.ev'];
fprintf('reading %s\n',filePath);
disp(filePath)
fileID = fopen(filePath,'r');
modal.eigen_length = fread(fileID,1,'int');
modal.modes_num = fread(fileID,1,'int');
modal.eigen_values = fread(fileID,modal.modes_num,'double');
for k = 1:modal.modes_num 
modal.eigen_vecs(:,k) = fread(fileID,modal.eigen_length,'double');
end
fclose(fileID);
%% Read .geo file
filePath = [root,'/',name,'.geo.txt'];
fprintf('reading %s\n',filePath);
map_with_coord = importdata(filePath,' ',1);
%% Get vmap
vmap = map_with_coord.data(:,1:2);
vmap = vmap+1;
%% Read tet file
filePath = [root,'/',name,'.tet'];
fprintf('reading %s\n',filePath);
fileID = fopen(filePath,'r');
tet.num_fixed_vertex = fread(fileID,1,'int');
tet.num_free_vertex = fread(fileID,1,'int');
for k = 1:tet.num_fixed_vertex
tet.fixed_vertex(k,:) = fread(fileID,3,'double');
end
tet.free_vertex = zeros(tet.num_free_vertex,3);
tet.free_vertex = fread(fileID,[tet.num_free_vertex,3],'double');
tet.num_tet = fread(fileID,1,'int');
tet.data = zeros(tet.num_tet,4,'int32');
tet.data = fread(fileID,[tet.num_tet,4],'int');
fclose(fileID);
%% Read in obj file
filePath = [root,'/',name,'.obj'];
fprintf('reading %s\n',filePath);
mesh.vertex = importdata(filePath,' ');
mesh.vertex = mesh.vertex.data;
mesh.face = importdata(filePath,' ',size(mesh.vertex,1)+3);
mesh.face=int32(mesh.face.data);
save([root,'/bem_input/mesh.mat'],'mesh');
%%
%To maksure the face normal point inward
mesh.face(:,[2,3]) = mesh.face(:,[3,2]);
%% test boundry normal direction
% fileID = fopen('test.obj','w');
% for v = 1:length(mesh.vertex)
%     fprintf(fileID,'v %f %f %f\n',mesh.vertex(v,1),mesh.vertex(v,2),mesh.vertex(v,3));
% end
% for f = 1:length(mesh.face)
%     fprintf(fileID,'f %d %d %d\n',mesh.face(f,1),mesh.face(f,2),mesh.face(f,3));
% end
% fclose(fileID);
% now 

%% Prepare dat file, using good parameters
%density = 3000;
%alpha = 1e-6;
%beta = 1.0;
fprintf('Calculating Freq:\n')
eigmodes = modal.eigen_values/density;
omega = sqrt(eigmodes);
c = alpha*eigmodes+beta;
x = c./(2.0*omega);
omegaD = omega.*(sqrt(1.0-x.*x));
freq = omegaD/(2*pi);
%% test for normal velocity
% prepare vmap for quick look up
[~,I] = sort(vmap(:,2));
vmap_lut = vmap(I,1);
%% vertex & header information are common
if exist([root,'/bem_input/init_bem.mat'],'file')==0 || exist([root,'/bem_input/init_bem.mat'],'file')==0 || overwrite==1
header = sprintf('acoustic radiation input data\nComplete 1 0\nFull 0 0.d0\n%d %d 0 0 1\n0 0\n0 0\n343 1.184 2d-5 1.d-12 0.\n'...
    ,size(mesh.face,1),size(mesh.vertex,1));
vertex_content='';
for vtxcnt = 1:size(mesh.vertex,1)
vertex_content = sprintf('%s%d %.15f %.15f %.15f\n',vertex_content,vtxcnt,mesh.vertex(vtxcnt,:));
end
init_bem = zeros(modal.modes_num,size(mesh.face,1));
for mode = 1:modal.modes_num
    % fast bem output
    filePath = [root,sprintf('/fastbem/input-%d.dat',mode-1)];
    fileID = fopen(filePath,'w');
    fprintf(fileID,header);
    fprintf(fileID,sprintf('%.15f %.15f 1 0 0\n',freq(mode),freq(mode)));
    fprintf(fileID,'0 3 1 0 One\n');
    fprintf(fileID,'$ Nodes\n');
    fprintf(fileID,vertex_content);
    fprintf(fileID,'$ Elements and Boundary Conditions:\n');
    fprintf('generating mode %d, with frequency %f \n',mode,freq(mode))
    for facecnt = 1:size(mesh.face,1)
    vtx = mesh.face(facecnt,:);
    coord = mesh.vertex(vtx,:);
    tet_vtxind = vmap_lut(vtx);
    eigenvec = modal.eigen_vecs(:,mode);
    eigen_amp = zeros(3,3);
    eigen_amp(:,1) = eigenvec((tet_vtxind-1)*3+1);
    eigen_amp(:,2) = eigenvec((tet_vtxind-1)*3+2);
    eigen_amp(:,3) = eigenvec((tet_vtxind-1)*3+3);
    mean_v = sum(eigen_amp*freq(mode))/3;
    a = coord(3,:)-coord(1,:);
    b = coord(2,:)-coord(1,:);
    normal_vec = cross(a,b);
    normal_vec = normal_vec/norm(normal_vec,2);
    init_value = sum(mean_v.*normal_vec);
    init_bem(mode,facecnt)=init_value;
    fprintf(fileID,'%d %d %d %d 2 (0, %.15f)\n',facecnt,vtx,init_value);
    end
    fprintf(fileID,'$ Field Points:\n$ Field Cells:\n$ End of file\n');
    fclose(fileID);
end
save([root,'/bem_input/init_bem.mat'],'init_bem');
save([root,'/bem_input/freq.mat'],'freq');

end
%%


%%
