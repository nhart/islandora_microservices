'''
Created on March 5, 2011

@author: jonathangreen
'''

from islandoraUtils.metadata.fedora_relationships import rels_int, rels_namespace, rels_ext
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
                DSC.mods_to_dc(obj, 'MODS', 'DC')
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
            #copy parent child policy to object being ingested
            try:
                if 'POLICY' not in 'obj':
                    relsext = rels_ext(obj, rels_namespace('fedora', 'info:fedora/fedora-system:def/relations-external#'), 'fedora')
                    relationship = relsext.getRelationships('isMemberOfCollection')
                    if relationship:
                        parent_pid = relationship[0][2]
                        parent_obj = client.getObject(parent_pid)
                        if parent_obj:
                            if 'CHILD_SECURITY' in parent_obj:
                                child_policy = parent_obj['CHILD_SECURITY']
                                policy_xml = child_policy.getContent().read()
                                obj.addDataStream('POLICY', policy_xml, controlGroup=u'M', label=u'Xacml Policy Stream', mimeType=u'text/xml', logMessage=u'Microservices added child policy to object')
                                self.logger.info('Copy CHILD_SECURITY datastream from parent. Pid %s' % message['pid'])
            except:
                pass
                self.logger.error('Can not copy CHILD_SECURITY datastream from parent. Pid %s' % message['pid'])
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
