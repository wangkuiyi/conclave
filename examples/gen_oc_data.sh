#!/bin/bash

write_data () {
sudo mkdir /mnt/bench/$1
sudo python3 gen_util.py /mnt/bench/$1/in1 2 $1 $1 'a,b'
}

sizes=( 15 150 300 450 600 750 900 1050 1200 1350 )

sudo mkdir /mnt/bench

for i in "${sizes[@]}"
do
  :
  write_data $i
done