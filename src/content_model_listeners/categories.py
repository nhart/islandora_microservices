'''
Created on Oct 19, 2010

@author: aoneill
'''


import tempfile, os, subprocess, logging
from urllib import quote

def get_datastream_as_file(obj, dsid, extension = ''):
    d = tempfile.mkdtemp()
    success = False
    tries = 10
    filename = '%(dir)s/content.%(ext)s' % {'dir': d, 'ext': extension}
    while not success and tries > 0:
        f =open(filename, 'w')
        f.write(obj[dsid].getContent().read())
        os.fsync(f.fileno())
        f.close()
        logging.debug("Size of datastream: %(size)d. Size on disk: %(size_disk)d." % {'size': obj[dsid].size, 'size_disk': os.path.getsize(filename)})
        if os.path.getsize(filename) != obj[dsid].size:
            tries = tries - 1
        else:
            success = True
    return d, 'content.'+extension

def update_datastream(obj, dsid, filename, label='', mimeType='', controlGroup='M'): 
    # Using curl due to an incompatibility with the pyfcrepo library.
    logging.debug("Updating datastream:")
    conn = obj.client.api.connection

    try:
        logging.debug("using curl to update object %(obj)s, datastream %(dsid)s, from file %(file)s" % {'obj': obj, 'dsid': dsid, 'file': filename})
        # this is a python 2.7 only function, so we shouldn't let this make it into the main sources
        # as everything else works on 2.6, but its very handy in this case.
        subprocess.check_output(['curl', '-i', '-H', '-XPOST', '%(url)s/objects/%(pid)s/datastreams/%(dsid)s?dsLabel=%(label)s&mimeType=%(mimetype)s&controlGroup=%(controlgroup)s'
                           % {'url': conn.url, 'pid': obj.pid, 'dsid': dsid, 'label': quote(label), 'mimetype': mimeType, 'controlgroup': controlGroup }, 
                           '-F', 'file=@%(filename)s' % {'filename': filename}, '-u', '%(username)s:%(password)s' % {'username': conn.username, 'password': conn.password}],
                           stderr=subprocess.STDOUT)
        r = 0
    except subprocess.CalledProcessError as e:
        logging.error('exception in curl call: ')
        logging.error(e.output)
        logging.error(str(e))
        r = 1
    except:
        logging.exception('exception in curl call')
        r = 1
    
    return r == 0

class FedoraMicroService(object):
    '''
    classdocs
    '''
    name = "Generic Microservice"
    content_model = "fedora-system:FedoraObject-3.0" 
    dsIDs = ['DC']    
    
    def runRules(self, obj, dsid, body):
        
        return 


    def __init__(self):
        '''
        Constructor
        '''
        