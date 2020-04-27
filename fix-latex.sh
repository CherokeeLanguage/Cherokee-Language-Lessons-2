#!/bin/bash

trap "echo ERROR; read a" ERR

set -e
set -o pipefail

if [ "$1"x = x ]; then
	echo "no file specificed!"
	read a
	exit -1
fi

sed -i 's@#LyX 2.1 created this file. For more info see http://www.lyx.org/@#LyX 2.2 created this file. For more info see http://www.lyx.org/@g' "$1"

sed -i 's@\\textclass extbook@\\save_transient_properties true\n\\origin unavailable\n\\textclass extbook@g' "$1"

sed -i 's@\\lyxformat 474@\\lyxformat 508@g' "$1"



