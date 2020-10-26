#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect

import logging, os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

cors_allowed_origins=[]

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', default='secret!')
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins=cors_allowed_origins)
thread = None
thread_lock = Lock()

@app.route('/control/<room>')
def route_regie(room):
    return render_template('regie.html',
                async_mode=socketio.async_mode,
                room = room,
                jitsi_room = f"studio_{room}",
                jitsi_domain = os.getenv('JITSI_DOMAIN', default='jitsi'),
                jitsi_password = os.getenv('JITSI_ROOM_PASSWORD', default=None),
            )


@app.route('/view/<room>')
def route_view(room):
    return render_template('viewonly.html',
                async_mode=socketio.async_mode,
                room = room,
                jitsi_silent = False,
                jitsi_room = f"studio_{room}",
                jitsi_domain = os.getenv('JITSI_DOMAIN', default='jitsi'),
                jitsi_password = os.getenv('JITSI_ROOM_PASSWORD', default=None),
            )

@app.route('/viewmuted/<room>')
def route_viewmuted(room):
    return render_template('viewonly.html',
                async_mode=socketio.async_mode,
                room = room,
                jitsi_silent = True,
                jitsi_room = f"studio_{room}",
                jitsi_domain = os.getenv('JITSI_DOMAIN', default='jitsi'),
                jitsi_password = os.getenv('JITSI_ROOM_PASSWORD', default=None),
            )

class RegieNamespace(Namespace):
    def on_my_broadcast_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             broadcast=True)

    def on_register(self, message):
        if message['type'] in ('user', 'worker'):
            session['type'] = message['type']
            session['room'] = message['room']
            if 'id' in message:
                session['id'] = message['id']
            join_room(f"{session['room']}_{session['type']}")
            emit('register', True)
            log.info('a %s joined room %s' % (session['type'], session['room']))
        else:
            log.error("got join request with unknown type: %s" % message['type'] )
            emit('register', False)

    def on_room(self, message):
        target_room = None
        if session['type'] == 'user':
            target_room = f"{session['room']}_worker"
        elif session['type'] == 'worker':
            target_room = f"{session['room']}_user"

        if target_room:
            if 'id' in session:
                message['source'] = session['id']
            log.info(f"sendung message to room {target_room}")
            emit('room', message, room=target_room)
        else:
            log.error("could not find target room in session for message.")


    def on_leave(self, message):
        leave_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_close_room(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                             'count': session['receive_count']},
             room=message['room'])
        close_room(message['room'])

    def on_room_message(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('room_message',
             {'data': message['data'], 'count': session['receive_count']},
             room=message['room'])

    def on_disconnect_request(self):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_ping(self):
        emit('pong')

    def on_connect(self):
        return

    def on_disconnect(self):
        print('Client disconnected', request.sid, session['type'])


socketio.on_namespace(RegieNamespace('/regie'))


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
