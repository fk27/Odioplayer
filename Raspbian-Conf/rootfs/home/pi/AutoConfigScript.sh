#!/bin/sh
#AutoConfigScript.sh

stepFile="step"

if [ ! -f $stepFile ]
then
    #echo "$0: File '${stepFile}' not found."
    echo "1">$stepFile
	echo "-> Init step file"
else
    echo "-> Step file found"
fi

read line < $stepFile

echo "-> Executing step: " $line

case $line in
	1)
		#Init Partition
		echo "-> Init Partition"
		(echo d; echo 2;
		echo n; echo p; echo 4; echo; echo;
		echo n; echo p; echo 2; echo; echo +5G;
		echo n; echo p; echo; echo;
		echo t; echo 3; echo c;
		echo d; echo 4;
		echo w;
		#echo p;
		)| sudo fdisk /dev/mmcblk0
		echo $((1+$line)) > $stepFile
		sudo reboot now
		;;
	2)
		#Init Linux file system to the max avaible space on partition
		echo "-> Init Linux file system space"
		sudo resize2fs /dev/mmcblk0p2
		echo $((1+$line)) > $stepFile
		sudo reboot now
		;;
	3)
		echo "-> Init Home directories"
		sudo -u pi bash -c 'mkdir /home/pi/music'
		sudo -u pi bash -c 'mkdir /home/pi/player'
		sudo -u pi bash -c 'mkdir /home/pi/sounds'

		echo "-> Init fstab"
		sudo echo -n "/dev/mmcblk0p3" >> /etc/fstab
		sudo echo -e -n "\t" >> /etc/fstab
		sudo echo -n "/home/pi/music" >> /etc/fstab
		sudo echo -e -n "\t" >> /etc/fstab
		sudo echo -n "vfat" >> /etc/fstab
		sudo echo -e -n "\t" >> /etc/fstab
		sudo echo -n "defaults" >> /etc/fstab
		sudo echo -e -n "\t" >> /etc/fstab
		sudo echo -n "0" >> /etc/fstab
		sudo echo -e -n "\t" >> /etc/fstab
		sudo echo "0" >> /etc/fstab

		echo $((1+$line)) > $stepFile
		sudo reboot now
		;;
	4)
		ping -q -c5 google.com > /dev/null

		if [ $? -eq 0 ]
		then
			echo "-> Init Raspbian packages"
			sudo apt-get -y -q  update

			echo "-> Purge Raspbian unnecessary  packages"
			sudo apt-get -y -q  purge libx11-6 libgtk-3-common xkb-data lxde-icon-theme raspberrypi-artwork

			echo "-> Install VLC"
			sudo apt-get -y -q  install vlc

			echo "-> Install pip3"
			sudo apt-get -y -q install python3-pip

			echo "-> Install python3-rpi.gpio"
			sudo apt-get -y -q install python3-rpi.gpio

			echo "-> Install beautifulsoup4"
			sudo pip3 -q install beautifulsoup4

			echo "-> Install Eyed3"
			sudo pip3 -q install Eyed3

			echo "-> Install python3-lxml"
			sudo apt-get -y -q install python3-lxml

			echo "-> Install python-vlc"
			sudo pip3 -q install python-vlc

			echo "-> Init Pimoroni pHatDac"
			sudo -u pi bash -c 'curl -sS https://get.pimoroni.com/phatdac | bash -s -- -y'

			echo "-> Init Samba"
			sudo apt-get -y -q install samba samba-common-bin

			echo "-> Init Samba user"
			(echo raspberry; echo raspberry;) | sudo smbpasswd -a -s pi

			echo "-> Samba smb.conf modification"
			sudo sed -i '/\[homes\]/,/^\[/ s/read only =.*/read only = no/' /etc/samba/smb.conf
			sudo sed -i '/\[homes\]/,/^\[/ s/create mask =.*/create mask = 0775/' /etc/samba/smb.conf
			sudo sed -i '/\[homes\]/,/^\[/ s/directory mask =.*/directory mask = 0775/' /etc/samba/smb.conf

			#echo "-> Samba restart"
			#sudo /etc/init.d/samba restart

			echo "-> Activate g_multi mode"
			sudo sed -i "/^g_.*$/ s|g_.*|g_multi|" /etc/modules

			echo "-> Init g_multi mass_storage"
			sudo echo "options g_multi file=/dev/mmcblk0p3 stall=0" > /etc/modprobe.d/g_multi.conf

			echo $((1+$line)) > $stepFile

			sudo reboot now

		else
			echo "Check the network connection!! no internet acces."
		fi
		;;
	*)
		echo "AutoConfigScript complete"
		;;
esac
