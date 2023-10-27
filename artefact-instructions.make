tar -xvf spot-2.11.6.tar.gz cd spot-2.11.6/
./configure --prefix ~/artefact-installs
cd ~/artefact-installs/spot-2.11.6/ && make && make-install

mv ~/*.tar.* ~/artefact-pkgs/ && cd ~/artefact-pkgs/
tar -xvf boost_1_82_0.tar.bz2
mv ~/artefact-pkgs/boost_1_82_0 ~/artefact-installs/
unzip meson-master.zip meson
export PATH="~/artefact-installs/meson/:$PATH"
export CPATH="~/artefact-installs/boost_1_82_0/:$CPATH"
export CPATH="~/artefact-installs/spot/:$CPATH"

sudo dpkg -i zsh-common_5.8.1-1_all.deb
sudo dpkg -i zsh_5.8.1-1_amd64.deb

spot libspot-dev spot-doc
libspot0 libspotltsmin0 libbddx-dev libbddx0 libspotgen0 
libspotltsmin0 fonts-mathjax libjs-mathjax libjs-requirejs

BOOST:
libboost-dev \
libboost1.74-dev \
libstdc++-11-dev \
gcc-11-base \
libc6-dev \
libc-dev-bin \
libc6 \
libcrypt1 \
libgcc-s1 \
gcc-12-base \
libcrypt-dev \
libnsl-dev \
libnsl2 \
libtirpc3 \
libgssapi-krb5-2 \
libcom-err2 \
libk5crypto3 \
libkrb5support0 \
libkrb5-3 \
libkeyutils1 \
libssl3 \
debconf \
perl-base \
dpkg \
tar \
libacl1 \
libselinux1 \
libpcre2-8-0 \
libbz2-1.0 \
liblzma5 \
libzstd1 \
zlib1g \
libtirpc-common \
libtirpc-dev \
linux-libc-dev \
rpcsvc-proto \
libgcc-11-dev \
libasan6 \
libatomic1 \
libgomp1 \
libitm1 \
liblsan0 \
libquadmath0 \
libtsan0 \
libubsan1 \
libstdc++6

GLIB:
libglib2.0-dev \
libffi-dev \
libffi8 \
libc6 \
libcrypt1 \
libgcc-s1 \
gcc-12-base \
libglib2.0-0 \
libmount1 \
libblkid1 \
libselinux1 \
libpcre2-8-0 \
libpcre3 \
zlib1g \
libglib2.0-bin \
libelf1 \
libglib2.0-data \
libglib2.0-dev-bin \
python3-distutils \
python3-lib2to3 \
python3:any \
libmount-dev \
libblkid-dev \
libc6-dev \
libc-dev-bin \
libcrypt-dev \
libnsl-dev \
libnsl2 \
libtirpc3 \
libgssapi-krb5-2 \
libcom-err2 \
libk5crypto3 \
libkrb5support0 \
libkrb5-3 \
libkeyutils1 \
libssl3 \
debconf \
perl-base \
dpkg \
tar \
libacl1 \
libbz2-1.0 \
liblzma5 \
libzstd1 \
libtirpc-common \
libtirpc-dev \
linux-libc-dev \
rpcsvc-proto \
uuid-dev \
libuuid1 \
libselinux1-dev \
libpcre2-dev \
libpcre2-16-0 \
libpcre2-32-0 \
libpcre2-posix3 \
libsepol-dev \
libsepol2 \
libpcre3-dev \
libpcre16-3 \
libpcre32-3 \
libpcrecpp0v5 \
libstdc++6 \
pkg-config \
libdpkg-perl \
perl:any \
zlib1g-dev

NINJA:
apt-rdepends ninja-build|grep -v "^ " |grep -v "^libc-dev$"
ninja-build libc6 libcrypt1 libgcc-s1 gcc-12-base libstdc++6