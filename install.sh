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
sed -i "/alias yum='dnfc'/d" /etc/bashrc
sed -i "/alias dnf='dnfc'/d" /etc/bashrc
echo "alias yum='dnfc'" >> /etc/bashrc
echo "alias dnf='dnfc'" >> /etc/bashrc



