function FMMsolver(cur_dir,overwrite)
PATH_TO_fmmlib3d = % should point to fmmlib3d/matlab
addpath(PATH_TO_fmmlib3d);
root = cur_dir;
prefix=[];
if exist([root,'/bem_input/mesh.mat'],'file') &&exist([root,'/bem_input',prefix,'/init_bem.mat'],'file') && exist([root,'/bem_input',prefix,'/freq.mat'],'file')

    load([root,'/bem_input/mesh.mat']);
    load([root,'/bem_input',prefix,'/init_bem.mat']);
    load([root,'/bem_input',prefix,'/freq.mat']);

else
     return
end

%%
[cent,nrm] = get_ctn(mesh.vertex,mesh.face);

ntri = length(mesh.face);
triangles = zeros(3,3,ntri);
for tri_id = 1:ntri
    v1 = mesh.face(tri_id,1);
    v2 = mesh.face(tri_id,2);
    v3 = mesh.face(tri_id,3);
    triangles(:,1,tri_id) = mesh.vertex(v1,:);
    triangles(:,2,tri_id) = mesh.vertex(v2,:);
    triangles(:,3,tri_id) = mesh.vertex(v3,:);
end



for mode = 1:length(freq)
    % system(['bash /data/vision/billf/object-properties/sound/ztzhang/renew/re_new.sh'])
    mode
    name = sprintf('output-%d.dat',mode-1);
    fprintf([root,'/bem_result',prefix,'/',name])
    
    if exist([root,'/bem_result',prefix,'/',name],'file') && overwrite==0
        continue
    end
    freq_cur= freq(mode);
    fprintf('solving b for mode %d(freq %4.3f): \n',mode,freq(mode));
    qs_fbem = init_bem(mode,:);

    
    iprec = 4;
    zk = 2*pi*freq_cur/343;
    rho = 1.184;
    init_velocity = 1i*qs_fbem.*(1i*2*pi*freq_cur*rho);
    
    tic
    [U]=hfmm3dtria(iprec,zk,ntri,triangles,nrm',cent',1,init_velocity.',0,0,nrm',1,0,0,0,0,0);
    toc
    
    b = U.pot/(4*pi);

    b = b.';

    
    Q = b./norm(b);
    s = norm(b);
    H=0;
    tol = 10^-3;
    %m=200;
    for n = 1:500
        % Arnoldi Iteration

         % Matrix * vec

        iprec=4;
        n
        tic
        [U]=hfmm3dtria(iprec,zk,ntri,triangles,nrm',cent',0,Q(:,n),1,Q(:,n),nrm',1,0,0,0,0,0);
        toc
        U.pot = U.pot/(4*pi);

        v = U.pot.' - Q(:,n)*0.5;



        H(:,n) = (v'*Q)';
        v = v - Q*H(:,n);
        H(n+1,n) = norm(v);
        % Update y
        temp_b = s*eye(n+1,1);

        y = H \(temp_b);
        r = norm(H*y-temp_b)/s;
        sprintf('residule: %f\n',norm(H*y-temp_b)/s)
        if r< tol
            x = Q*y;
            fprintf('RETURN!!!\n')
            break
        end
        Q(:,n+1)= v/H(n+1,n);
    end
  

     fprintf('WRITING!!!\n')
     ps_num = -x;
     
     fileID = fopen([root,'/bem_result',prefix,'/',name],'w+');
     fprintf(fileID, '  Freq. No. =   1,  f = %1.4s (Hz),  k = (0.1832D+01, 0.0000D+00):\n',freq(mode));
     fprintf(fileID, ' Solution on the Boundary:\n');
     fprintf(fileID, 'Elements: this line is just for fun \n');
     for k = 1:length(ps_num)
         fprintf(fileID,sprintf('%d ( %1.6s , %1.6s ) \n',k,real(ps_num(k)),imag(ps_num(k))));
     end
     fclose(fileID);
end

end

