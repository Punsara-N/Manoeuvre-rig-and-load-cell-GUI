import io

filename = 'HELLO.csv' 
dest = io.BufferedWriter(io.FileIO(filename, 'w'))
dest.write('HIIII, 123, 523')