rm /usr/bin/dnfc
rm -r /usr/share/dnfc
sed -i "/alias yum='dnfc'/d" /etc/bashrc
sed -i "/alias dnf='dnfc'/d" /etc/bashrc

