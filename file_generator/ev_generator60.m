function ev_generator60(name,num)
%.ev file generator
%   Load stiffness and mass matrices and output eigenvalues and
%   eigenvectors into .ev file

    K = readSPM([name,'.stiff.spm']);
    M = readSPM([name,'.mass.spm']);
    outfile = [name,'.ev'];
    shift = 7;
    [r, ~] = size(M);
    [V, D] = eigs(K,M,num+shift,'sm');
    
    fileID = fopen(outfile, 'w+');
    logID = fopen('log.txt', 'w+');
    fwrite(fileID, r, 'int');
    fwrite(fileID, num, 'int');
    D=flip(diag(D));
    V=fliplr(V);
    fprintf('Eigen Value calculated.s')
    for i = shift+1:num+shift
        fprintf (logID,'%3.8s \n',[D(i)]);
    end
        fclose(logID);
    for i = shift+1:num+shift
        fwrite(fileID, D(i), 'double');
    end
    for i = shift+1:num+shift
        fwrite(fileID, transpose(V(:,i)), 'double');
    end
    fclose(fileID);
end
