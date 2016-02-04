# =============================================================================
# session.py
#
# Do the twisted stuff required to get a per-session record of the two things
# we care about: the persistent connection to the server, and the queue of JSON
# objects waiting to be pushed to the client via ajax.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from zope.interface import Interface, Attribute, implements
from twisted.python.components import registerAdapter
from twisted.web.server import Session

class SessionData(object):
    """
    Per-session data we care about. @@@ not multi-tab safe yet
    """
    def __init__(self):
        self.connection_state = 'disconnected' # or 'connecting' or 'connected'
        self.transport_tx_cb = None
        self.transport_rx_cb = None
        self.transport_dropped_cb = None
        self.transport_drop_cb = None
        self.push_queue = []
        self.pending_req_dispatch_fn = None

    def set_conn_state(self, state):
        self.log('Changing connection state from {} to {}'.format(
            self.connection_state, state))
        # uncomment to see how we got here
        #import traceback
        #traceback.print_stack()
        self.connection_state = state
        self.add_to_push_queue('connection_state', state=state)

    def log(self, msg):
        print('### LOG:', msg)
        self.add_to_push_queue('log', msg=msg)

    def alert(self, msg):
        print('### ALERT:', msg)
        self.add_to_push_queue('alert', msg=msg)

    def highlight(self, selector):
        print('### HIGHLIGHT:', selector)
        self.add_to_push_queue('highlight', selector=selector)

    def set_text(self, selector, text):
        print('### SET TEXT: {} -> {}'.format(selector, text))
        self.add_to_push_queue('set_text', selector=selector, text=text)

    def set_html(self, selector, html):
        print('### SET HTML: {} -> {}'.format(selector, html))
        self.add_to_push_queue('set_html', selector=selector, html=html)

    def add_to_push_queue(self, fn, **kwargs):
        item = {'fn': 'handle_' + fn}
        for k, v in kwargs.items():
            item[k] = v
        self.push_queue.append(item)
        if self.pending_req_dispatch_fn:
            fn = self.pending_req_dispatch_fn
            self.pending_req_dispatch_fn = None
            fn(self.drain_push_queue())

    def drain_push_queue(self):
        pq = self.push_queue
        self.push_queue = []
        return pq

    def restore_push_queue(self, pq):
        pq.extend(self.push_queue)
        self.push_queue = pq

    def add_pending_push_queue_dispatch(self, fn):
        if self.pending_req_dispatch_fn is not None:
            print('### overwriting pending_req_dispatch_fn')
        self.pending_req_dispatch_fn = fn

    def remove_pending_push_queue_dispatch(self):
        assert self.pending_req_dispatch_fn is not None
        self.pending_req_dispatch_fn = None

class ISessionData(Interface):
    sdata = Attribute("Per-session data object")

class CreateSessionData(object):
    """
    Create a per-session data object used by M2M
    """
    implements(ISessionData)
    def __init__(self, session):
        self.sdata = SessionData()

registerAdapter(CreateSessionData, Session, ISessionData)

def get_data(request):
    """
    Return the per-session dict related to this request
    """
    session = request.getSession()
    return ISessionData(session).sdata
