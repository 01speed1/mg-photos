#!/bin/bash
cargo clean && \
cargo build --release && \
/mnt/c/Users/O1spe/Desktop/platform-tools/adb.exe shell "rm -rf /data/local/tmp/mg-photos" && \
./deploy.sh &&\
/mnt/c/Users/O1spe/Desktop/platform-tools/adb.exe shell "LD_DEBUG=1 /data/local/tmp/mg-photos"