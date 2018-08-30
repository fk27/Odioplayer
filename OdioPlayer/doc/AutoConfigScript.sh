#Auto config script
====================

#remove unnecessary lib for desktop
#====================================
sudo apt-get -y purge libx11-6 libgtk-3-common xkb-data lxde-icon-theme raspberrypi-artwork

#player libs
#============
sudo apt-get -y install Eyed3
sudo apt-get install vlc

#for python2
#============
sudo apt-get -y install python-pip
sudo apt-get -y install python-rpi.gpio
sudo pip install beautifulsoup4
sudo pip install Eyed3
sudo apt-get -y install python-lxml
sudo pip install python-vlc

#for python3
#============
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-rpi.gpio
sudo pip3 install beautifulsoup4
sudo pip3 install Eyed3
sudo apt-get -y install python3-lxml
sudo pip3 install python-vlc