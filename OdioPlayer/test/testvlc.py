
import requests
import vlc
from time import sleep
'''
urls = [
    'http://network.absoluteradio.co.uk/core/audio/aacplus/live.pls?service=acbb',
    'file:///home/rolf/test.m3u',
    'file:///home/rolf/happy.mp3',
    'http://statslive.infomaniak.ch/playlist/energy90s/energy90s-high.mp3/playlist.pls',
    'http://streaming.radio.rtl2.fr/rtl2-1-44-128',
    ]
'''
urls = ['FeelTheLoveGo.wav']
playlists = set(['pls','m3u','wav'])

Instance = vlc.Instance()

for url in urls:
    ext = (url.rpartition(".")[2])[:3]
    test_pass = False    
    try:
        if url[:4] == 'file':
            test_pass = True
        else:
            r = requests.get(url, stream=True)
            test_pass = r.ok
    except Exception as e:
        print('failed to get stream: {e}'.format(e=e))
        test_pass = False
    else:
        if test_pass:
            print('Sampling for 15 seconds')
            player = Instance.media_player_new()
            Media = Instance.media_new(url)
            Media_list = Instance.media_list_new([url])
            Media.get_mrl()
            player.set_media(Media)
            if ext in playlists:
                list_player = Instance.media_list_player_new()
                list_player.set_media_list(Media_list)
                if list_player.play() == -1:
                    print ("Error playing playlist")
            else:
                if player.play() == -1:
                    print ("Error playing Stream")
            sleep(15)
            if ext in playlists:
                list_player.stop()
            else:
                player.stop()

        else:
            print('error getting the audio')