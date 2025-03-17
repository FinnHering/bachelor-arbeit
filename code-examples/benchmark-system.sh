#!/bin/bash -l


hostname 1>&2

. ~/julea/scripts/environment.sh 1>&2

export JULEA_CONFIG="$(hostname)"

julea-config --user --name="$(hostname)"  --object-servers="$(hostname)" --kv-servers="$(hostname)" --db-servers="$(hostname)"   --object-backend=posix --object-path="/tmp/julea-$(id -u)/posix"   --kv-backend=lmdb --kv-path="/tmp/julea-$(id -u)/lmdb"   --db-backend=sqlite --db-path="/tmp/julea-$(id -u)/sqlite" 1>&2

./julea/scripts/setup.sh clean-local 1>&2

# prepare the environment
./julea/scripts/setup.sh start-local 1>&2

# run the benchmark
./julea/scripts/benchmark.sh -m -d 13

# clean up the environment
./julea/scripts/setup.sh stop-local 1>&2