# Raspbian Configuration
1. Download the last raspbian lite image
2. Copy the image on an micro sd card with a tool like "etcher"
3. launch InitRaspbianSDcard.bat to copy the setup files (after copying unmount drive carrefully)
4. Put the micro sd card in a raspberry pi zero and boot
5. Connect with putty to raspberrypi.local
    > for windows, install "Bonjour Print Services for Windows v2.0.2", to be able to ping raspberrypi.local
	https://support.apple.com/kb/DL999?locale=en_US
6. Run the script AutoConfigScript.sh (after reboot manually run it again until setup completed)
	> sudo sh AutoConfigScript.sh
7. Copy some music files on the OdioPlayer Drive (a drive must appear on your computer)
8. Connect with putty and Start the player
    > sh startPlayer.sh
    
9. To start the player as a service:
    > check that OdioPlayer.service is present in /etc/systemd/system
    
    > systemctl is-active OdioPlayer.service
    
    > sudo systemctl enable OdioPlayer.service
    
    > sudo systemctl start OdioPlayer.service
     
    > sudo systemctl stop OdioPlayer
    
    > sudo systemctl disable OdioPlayer

