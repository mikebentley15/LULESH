#!/bin/bash

set -e
set -x

# clone FLiT and LULESH into /tmp/bentley8
mkdir /tmp/bentley8
cd /tmp/bentley8
git clone --branch lulesh-dev https://github.com/PRUNERS/FLiT.git
git clone --branch flit-tests https://github.com/mikebentley15/LULESH.git

# Compile FLiT and put the python script in the front of the PATH
make --directory FLiT \
  CXX=../LULESH/flit-tests/corrupt_clang.py -j10
mkdir bin
ln -s ../FLiT/scripts/flitcli/flit.py bin/flit
export PATH=/tmp/bentley8/bin:$PATH

# Profile all of the LULESH code.  This was put into the 'dev' target
# see flit-config.toml to see how
cd LULESH/flit-tests
flit update
make dev -j10

# Create the database of corruptions to use in the experiment
./create_corrupt_db.py \
  --test LuleshTest \
  --seed 42 \
  --all \
  --all-ops \
  --output corruptions.sqlite \
  tests/lulesh-wrap.cpp.prof \
  lulesh-comm.cpp.prof \
  lulesh-init.cpp.prof \
  lulesh-util.cpp.prof \
  lulesh-viz.cpp.prof

PROCESSOR_COUNT=$(grep processor /proc/cpuinfo | wc -l)

# Run the experiment
# Note the --delete flag, it deletes non-needed files as it goes
flit bisect \
  --auto-sqlite-run corruptions.sqlite \
  --delete \
  --parallel $PROCESSOR_COUNT \
  --jobs 5

# Capture the results and save them
RESULTS_DIR=lulesh-ray-bisect-inject
PROF_DIR=$RESULTS_DIR/prof-files
mkdir -p $PROF_DIR
cp -r bisect-* $RESULTS_DIR/
cp corruptions.sqlite $RESULTS_DIR/
cp auto-bisect.csv $RESULTS_DIR/
cp tests/*.prof $PROF_DIR/
cp *.prof $PROF_DIR/
find $RESULTS_DIR/ -type f -name \*.o -delete
find $RESULTS_DIR/ -type f -name \*.d -delete
find $RESULTS_DIR/ -type f -executable -delete
tar -czf ${RESULTS_DIR}.tgz $RESULTS_DIR
cp ${RESULTS_DIR}.tgz $HOME/

# Delete the stuff we made
cd /tmp
rm -rf bentley8

