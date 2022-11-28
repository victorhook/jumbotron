#from videoplayer import VideoPlayer, AudioPlayer


#player = VideoPlayer(20, 'images', 'audio.wav')
#player.start()


#AudioPlayer('audio.wav').start()

from client import Client
c = Client()
c.connect()
c.play_audio('audio.wav')
c.disconnect()