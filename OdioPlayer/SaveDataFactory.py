from ButtonType import ButtonType

def MemCurrentAlbum (self, btnType):
    print("btnType: "+ ButtonType.toString(btnType).lower())
    print("-> MemCurrentAlbum:"+str(self.currentAlbumId)+" "+str(self.currentTrackId))
    if self.savedDataFile.closed:
        self.savedDataFile = open(self.savedDataFile.name,"r+")

    if btnType == ButtonType.M1:
        self.savedData.m1.albumId.string=str(self.currentAlbumId)
        self.savedData.m1.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.m1.trackId.string=str(self.currentTrackId)
        self.savedData.m1.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
    elif btnType == ButtonType.M2:
        self.savedData.m2.albumId.string=str(self.currentAlbumId)
        self.savedData.m2.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.m2.trackId.string=str(self.currentTrackId)
        self.savedData.m2.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
    elif btnType == ButtonType.M3:
        self.savedData.m3.albumId.string=str(self.currentAlbumId)
        self.savedData.m3.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.m3.trackId.string=str(self.currentTrackId)
        self.savedData.m3.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
    elif btnType == ButtonType.M4:
        self.savedData.m4.albumId.string=str(self.currentAlbumId)
        self.savedData.m4.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.m4.trackId.string=str(self.currentTrackId)
        self.savedData.m4.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
        
    self.savedDataFile.seek(0)
    self.savedDataFile.truncate()
    self.savedDataFile.write(self.savedData.prettify())
    self.savedDataFile.close()

def SaveCurrentTrackPosition (self):
    #print("-> SaveCurrentTrackPosition")

    postion = self.player.get_position()

    if self.savedDataFile.closed:
        self.savedDataFile = open(self.savedDataFile.name,"r+")

    self.savedData.lastTrackPosition.string=str(postion)

    self.savedDataFile.seek(0)
    self.savedDataFile.truncate()
    self.savedDataFile.write(self.savedData.prettify())
    self.savedDataFile.close()

    return postion

def SaveCurrentAlbumAndTrack (self):
    print("-> SaveCurrentAlbumAndTrack")
    if self.savedDataFile.closed:
        self.savedDataFile = open(self.savedDataFile.name,"r+")

    self.savedData.lastAlbumId.string=str(self.currentAlbumId)
    self.savedData.lastAlbumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
    self.savedData.lastTrackId.string=str(self.currentTrackId)
    self.savedData.lastTrackTitle.string=str(self.currentTrackList[self.currentTrackId])

    self.savedDataFile.seek(0)
    self.savedDataFile.truncate()
    self.savedDataFile.write(self.savedData.prettify())
    self.savedDataFile.close()

def SaveCurrentVolume (self):
    print("-> SaveCurrentVolume: "+str(self.currentVolume))
    if self.savedDataFile.closed:
        self.savedDataFile = open(self.savedDataFile.name,"r+")

    self.savedData.currentVolume.string = str(self.currentVolume)

    self.savedDataFile.seek(0)
    self.savedDataFile.truncate()
    self.savedDataFile.write(self.savedData.prettify())
    self.savedDataFile.close()
