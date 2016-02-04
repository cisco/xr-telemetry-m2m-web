# =============================================================================
# render_push_queue.py
#
# This file implements pushing data to the client over AJAX.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import exceptions, json
from twisted.web import server
from m2m_demo.frontend import RegisterPage, BaseResource

class PushQueuePage(BaseResource):
    '''
    Serve up the push queue
    '''
    def render_POST(self, request):
        request.setHeader('Content-Type', 'application/json')
        pq = request.sdata.drain_push_queue()
        if len(pq) > 0:
            return json.dumps(pq)
        else:
            def finish_later(pq):
                try:
                    request.write(json.dumps(pq))
                    request.finish()
                except exceptions.RuntimeError as e:
                    print("### can't send push queue: ", e)
                    request.sdata.restore_push_queue(pq)
            request.sdata.add_pending_push_queue_dispatch(finish_later)
            request.notifyFinish().addErrback(lambda _: request.sdata.remove_pending_push_queue_dispatch())
            return server.NOT_DONE_YET

page = RegisterPage(PushQueuePage, '/push_queue')
