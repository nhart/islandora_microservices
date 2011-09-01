
from plugin_manager import IslandoraListenerPlugin as ILP
from islandoraUtils import DSConverter as CONV

class fjm(ILP):
    def fedoraMessage(self, message, obj, client):
        if message['dsid']:
            if message['dsid'] == 'PDF':
                CONV.create_swf(obj, 'PDF', 'SWF')
                CONV.create_thumbnail(obj, 'PDF', 'temp')
            elif message['dsid'] == 'JPG':
                CONV.create_thumbnail(obj, 'JPG', 'temp')
            elif message['dsid'] == 'MARCXML':
                pass
            elif message['dsid'] == 'WAV':
                CONV.create_mp3(obj, 'WAV', 'MP3')
            

    def islandoraMessage(self, method, message, client):
        pass
