#!/bin/bash
cd /mnt/shared/
./sm_compile_to_remote.sh /mnt/shared/ssn_hybrid/secrec/shark_join_2.sc
./Submitter --bytecode shark_join_2.sb --rels-meta joined:3 --output-path /mnt/shared/ssn_hybrid/data
