function M = readSPM(file)
%file = 'test_cube.mass.spm';
fid = fopen(file,'r');
data = fread(fid,1,'uchar');
h = fread(fid,1,'int');
w = fread(fid,1,'int');
fprintf('reading %s\n size: %d x %d\n',file,w,h)
n = fread(fid,1,'int');
r = zeros(1,n);
c = zeros(1,n);
v = zeros(1,n);
for k = 1:n
   r(k) = fread(fid,1,'int');
   c(k) = fread(fid,1,'int');
   v(k) = fread(fid,1,'double');
end

M = sparse(r,c,v);
fprintf('reading finished');