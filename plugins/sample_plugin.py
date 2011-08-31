
from plugin_manager import IslandoraListenerPlugin

class sample_plugin(IslandoraListenerPlugin):

    def fedoraMessage(self, message, obj, client):
        print message
        print obj.pid
        print ""

    def islandoraMessage(self, method, message, client):
        print method
        print message
        print ""
        
