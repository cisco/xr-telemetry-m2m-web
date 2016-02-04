
# =============================================================================
# ssh.py
#
# This file implements the SSH connection between server and router.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import exceptions, re

from twisted.internet import defer, reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.conch.ssh.keys import Key
from twisted.conch.endpoints import SSHCommandClientEndpoint

class LineProtocol(Protocol):
    """
    The JSON-RPC server sends individual stanzas as separate lines. So
    the protocol we apply here is line-in/line-out, and let the JSON-RPC
    layer interpret these.
    """
    def __init__(self):
        self.data = ''
        self.got_date = False

    def connectionMade(self):
        sdata = self.factory.sdata
        sdata.transport_tx_cb = self.sendLine
        sdata.set_conn_state('connected')
        sdata.log('line protocol up')
        def disconnect():
            # replaces the one in connect() below once the connection is up
            sdata.log('Disconnecting once connected by request')
            self.transport.loseConnection()
        sdata.transport_drop_cb = disconnect

    def dataReceived(self, data):
        sdata = self.factory.sdata
        sdata.log('rx ssh data="{}"'.format(data))
        self.data += data
        if '\n' in self.data:
            lines = re.split('[\r\n]+', self.data)
            self.data = lines[-1]
            for line in lines[:-1]:
                if len(line) > 0:
                    if self.got_date:
                        sdata.transport_rx_cb(line)
                    else:
                        sdata.log('ssh ignoring date: {}'.format(line))
                        self.got_date = True

    def connectionLost(self, reason):
        sdata = self.factory.sdata
        sdata.set_conn_state('disconnected')
        sdata.log('discarding partial rx data "{}"'.format(self.data))
        sdata.transport_dropped_cb()

    def sendLine(self, line):
        sdata = self.factory.sdata
        if sdata.connection_state != 'connected':
            sdata.log('ignoring tx data since not connected: "{}"'.format(line))
        else:
            return self.transport.write(line + '\n')

class PermissiveKnownHosts(object):
    """Override the usual knownHosts behavior and just permit anything."""
    def verifyHostKey(self, ui, hostname, ip, key):
        return defer.succeed(True)

def push_failure_message(reason, sdata):
    """
    Inform the client about an exception
    """
    try:
        full_reason = str(reason)
        m = re.search('<.*>: *(.+)', full_reason)
        readable_reason = m.group(1) if m else full_reason
        sdata.set_conn_state('disconnected')
        sdata.set_text('#connection_failure_reason',
                       'Connection failed: ' + readable_reason)
        sdata.log('connect error ' + full_reason)
    except Exception as e:
        # if we fluff up the exception handling, at least leave a clue
        print('### Failed exception handling', str(e))

def connect(sdata, command, username, host, port=22, key_file=None, password=None):
    """
    Connect to an SSH host (as it happens, persistently).
    """
    sdata.set_conn_state('connecting')

    try:
        keys = [Key.fromFile(key_file)] if key_file else None
    except exceptions.IOError as e:
        print('### key load error:', str(e))
        push_failure_message(str(e), sdata)
        return

    endpoint = SSHCommandClientEndpoint.newConnection(
                    reactor, command, username, host, port=int(port),
                    keys=keys, password=password, ui=None,
                    knownHosts=PermissiveKnownHosts())

    factory = Factory()
    factory.protocol = LineProtocol
    factory.sdata = sdata

    d = endpoint.connect(factory)

    # Very small race condition between here and the replacement
    # in connectionMade() above, but I've never managed to hit it.
    def disconnect():
        sdata.log('Disconnecting while still attempting to connect, by request')
        d.cancel()
    sdata.transport_drop_cb = disconnect

    d.addErrback(lambda reason: push_failure_message(reason, sdata))
    return d
