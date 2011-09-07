
from plugin_manager import IslandoraListenerPlugin as ILP
from islandoraUtils import DSConverter as CONV
import logging

class fjm(ILP):
    def __init__(self):
        self.logger = logging.getLogger('IslandoraListenerPlugin.fjm')

    def fedoraMessage(self, message, obj, client):
        logger = self.logger
        logger.debug(message)
        if message['dsid']:
            if message['dsid'] == 'PDF':
                CONV.create_swf(obj, 'PDF', 'SWF')
                CONV.create_thumbnail(obj, 'PDF', 'TN')
            elif message['dsid'] == 'JPG':
                CONV.create_thumbnail(obj, 'JPG', 'TN')
            elif message['dsid'] == 'MARCXML':
                CONV.marcxml_to_mods(obj, 'MARCXML', 'MODS')
            elif message['dsid'] == 'WAV':
                CONV.create_mp3(obj, 'WAV', 'MP3')
            

    def islandoraMessage(self, method, message, client):
        pass
