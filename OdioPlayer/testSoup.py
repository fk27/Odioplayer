# encoding=utf8  
import sys  
from bs4 import BeautifulSoup

reload(sys)  
sys.setdefaultencoding('utf8')

print("ici1")
configFile = open("/home/pi/player/config.xml")
print("ici2")
config = BeautifulSoup(configFile,'lxml')
print("ici3")
