if [ ! -d "/usr/share/dnfC" ]; then
	mkdir /usr/share/dnfC
fi
if [ ! -d "/usr/share/dnfC/spdx" ]; then
	mkdir /usr/share/dnfC/spdx
fi
cp bin/dnfc /usr/bin/

for file in src/*; do
    if [ -f $file ]; then
		cp $file /usr/share/dnfC
	fi
done
for file in src/spdx/*; do
    if [ -f $file ]; then
		cp $file /usr/share/dnfC/spdx
	fi
done
#/usr/bin/apt -y install python3 python3-pip python3-loguru python3-pycurl python3-certifi python3-wget python3-lz4
#echo "alias apt='aptc'" > /etc/profile.d/aptc-hook.sh
alias apt='aptc'


