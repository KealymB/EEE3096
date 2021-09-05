for x in "-O0" "-O1" "-O2" "-O3" "-Ofast" "-Os" "Og" "-funroll-loops"
do
CFLAGS="-lm -lrt $x" make
make run
done
