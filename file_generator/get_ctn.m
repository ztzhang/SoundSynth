function [cent,nrm] = get_ctn(r_nodes,r_elem)
    cent = zeros(length(r_elem),3);
    nrm = zeros(length(r_elem),3);
    for k = 1:length(r_elem)
        vtx = r_elem(k,1:3);
        coord = r_nodes(vtx,:);
        cent(k,:) = sum(coord)/3;
        a = coord(1,:);
        b = coord(2,:);
        c = coord(3,:);
        nm = cross(b-a,c-a);
        nrm(k,:)=nm/norm(nm);
    end
end