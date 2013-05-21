'''
Created on March 5, 2011

@author: jonathangreen
'''

from islandoraUtils.metadata.fedora_relationships import rels_int, rels_namespace
from plugin_manager import IslandoraListenerPlugin
from fcrepo.connection import FedoraConnectionException
from coalliance_mime import CoallianceMime
from islandoraUtils.metadata.fedora_relationships import rels_int, rels_namespace, rels_object
from islandoraUtils import DSConverter as DSC
import coalliance_metadata
import json
import re

class coalliance(IslandoraListenerPlugin):

    def processMessage(self, dsid, obj, comime):
        try:
            # do actions based on DSID then on MIME
            if dsid == 'MODS':
                coalliance_metadata.add_handle_to_mods(obj)
            elif dsid == 'TN':
                pass
            elif dsid == 'POLICY':
                coalliance_metadata.add_policy_to_rels(obj)
            else:
                comime.dispatch(dsid)

        except FedoraConnectionException:
            self.logger.warning('Object %s does not exist.' % obj.pid)

    def fedoraMessage(self, message, obj, client):
        # if this is a ingest method, then we want to do actions for each datastream
        comime = CoallianceMime(obj)
        if message['method'] == 'ingest':
            for dsid in obj:
                self.processMessage(dsid, obj, comime)
        # clean up the rels if this was a purge
        elif message['method'] == 'purgeDatastream':
            relsint = rels_int(obj, rels_namespace('coal', 'http://www.coalliance.org/ontologies/relsint'), 'coal')
            relsint.purgeRelationships(subject=message['dsid'])
            relsint.purgeRelationships(object=message['dsid'])
            relsint.update()
        # else we just mess with the one that was changed
        elif message['dsid']:
            self.processMessage(message['dsid'], obj, comime)

    def islandoraMessage(self, method, message, client):
        if method == 'generateDerivatives':
            if 'pid' not in message:
                self.logger.error("No PID passed in message.")
            try:
                obj = client.getObject(message['pid'])
                comime = CoallianceMime(obj)
                for dsid in obj:
                    self.processMessage(dsid, obj, comime)
                if 'TN' not in obj:
                    self.logger.info('No TN datastream on object, attempting to find a derivative to copy')
                    for dsid in obj:
                        if re.search(".*-tn.jpg\Z", dsid, 0):
                            try:
                                self.logger.info('Creating TN DS from %s .' % dsid)
                                comime.create_thumbnail(obj, dsid, 'TN')
                                break;
                            except:
                                self.logger.exception('Could not create TN Datastream from %s .' % dsid)
            except:
                self.logger.exception('Pid does not exist. Pid %s' % message['pid'])
            self.logger.info('Derivative generation process complete for PID: %s' % message['pid'])
        elif method == 'regenerateDerivatives':
            if 'pid' not in message:
                self.logger.error("No PID passed in message.")
            try:
                obj = client.getObject(message['pid'])
                try:
                    obj['TN'].delete()
                except:
                    pass
                relsint = rels_int(obj, rels_namespace('coal', 'http://www.coalliance.org/ontologies/relsint'), 'coal')
                relationships = relsint.getRelationships()
                try:
                    obj['RELS-INT'].delete()
                except:
                    pass
                for relationship in relationships:
                    try:
                        obj[relationship[2].data].delete()
                    except:
                        pass
		self.stomp.send('/topic/islandora', json.dumps(message), {'method' : 'generateDerivatives'})
            except:
                self.logger.exception('Pid does not exist. Pid %s' % message['pid'])
