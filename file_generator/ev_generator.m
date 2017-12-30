function ev_generator(stiffness_matrix, mass_matrix, fmin, fmax, density, outfile )
%.ev file generator
%   Load stiffness and mass matrices and output eigenvalues and
%   eigenvectors into .ev file

    K = spconvert(importdata(stiffness_matrix));
    M = spconvert(importdata(mass_matrix));
    
    [r, ~] = size(M);
    [V, D] = eigs(K,M,r-1);
    [upper, lower] = find_cutoff(D, fmax, fmin, density);
    display([upper, lower]);
    
    fileID = fopen(outfile, 'a+');
    fwrite(fileID, r, 'int');
    fwrite(fileID, lower-upper+1, 'int');
    for i = upper:lower
        disp(i);
        fwrite(fileID, D(i,i), 'double');
    end
    for i = upper:lower
        fwrite(fileID, transpose(V(:,i)), 'double');
    end
end

function [upper,lower] = find_cutoff( D, fmax, fmin, density)
    lambda = diag(D);
    upper_lambda = (2*pi*fmax)^2*density;
    lower_lambda = (2*pi*fmin)^2*density;
    display([upper_lambda, lower_lambda]);
    result = find(lambda<upper_lambda & lambda>lower_lambda);
    upper = result(1);
    lower = result(end);
end