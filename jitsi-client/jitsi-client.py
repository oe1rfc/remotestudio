import argparse
from os import environ as env
import logging
import signal

import socketio
from jibriselenium import JibriSeleniumDriver

logging.basicConfig(level=env.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

# add to .jitsi-meet-cfg/web/config.js: hiddenDomain: 'recorder.meet.jitsi',


sio = socketio.Client()

@sio.event
def connect():
    log.info("I'm connected!")

@sio.event
def connect_error():
    log.error("The connection failed!")

@sio.event
def disconnect():
    log.warning("I'm disconnected!")



class JitsiNamespace(socketio.ClientNamespace):
    def __init__(self, namespace, roomname, worker_id, 
                  jitsi_url, jitsi_email, displayname, xmpp_login, xmpp_password, **kwargs):
        socketio.ClientNamespace.__init__(self, namespace)
        self.worker_id = worker_id
        self.namespace = namespace
        self.roomname = roomname
        self.ws_connected = False
        self.status = 'disconnected'

        self.jitsi = None
        self.jitsi_room = None
        self.jitsi_url = jitsi_url
        self.jitsi_email = jitsi_email
        self.displayname = displayname
        self.xmpp_login = xmpp_login
        self.xmpp_password = xmpp_password

        self.options = kwargs

    @property
    def jitsi_connected(self):
        return self.status == 'connected'

    def start_jitsi(self):
        self.log_info("starting jitsi browser")
        self.jitsi = JibriSeleniumDriver(self.jitsi_url,
                displayname = self.displayname,
                email = self.jitsi_email,
                xmpp_login = self.xmpp_login,
                xmpp_password = self.xmpp_password
            )
    def stop_jitsi(self):
        if self.jitsi:
            self.jitsi.quit()
            self.jitsi = None
        
    def launch(self, room, url=None):
        if not self.jitsi:
            self.start_jitsi()
        if url:
            self.jitsi_url = url
        self.jitsi_room = room
        room_url = f"{ self.jitsi_url.rstrip('/') }/{ room }"
        self.log_info("launching %s" % room_url)
        self.jitsi.launchUrl(room_url)
        self.jitsi.waitXMPPConnected()

    def hide_ui_elements(self):
        self.jitsi.execute_script("""
            $(".filmstrip__toolbar > button").click();
            $(".filmstrip__toolbar").hide();
            $(".large-video-labels").hide();
            $("#new-toolbox").hide();
            $("#videoconference_page > .subject").hide();
            $(".atlaskit-portal div").hide();
            $("#filmstripLocalVideo").hide();
            $("#localVideoTileViewContainer").hide();
            $('span.videocontainer > div').hide();
            $('span.videocontainer > span').hide();
            APP.conference.localAudio.mute();
            """)

    def quit(self):
        self.jitsi.quit()

    def log_info(self, msg):
        # TODO also send to websocket
        log.info(msg)


    def on_connect(self):
        self.emit('register', {'type': 'worker', 'room': self.roomname, 'id': self.worker_id});

    def on_register(self, status):
        self.ws_connected = status
        log.info("on_register status: %s" % status)
        #self.send_room([], 'jitsi') # clear participants in clients
        self.send_update() # clear participants in clients

    def on_disconnect(self):
        self.ws_connected = False
        log.warning("Disconnected!")

    def on_room(self, data):
        if 'command' in data:
            cmd = data['command']
            cmd_data = None
            if 'id' in data and data['id'] != self.worker_id:
                log.info('command ignored for %s' % data['id'])
                return
            log.info('command for us: %s' % data)
            if 'data' in data:
                cmd_data = data['data']
            handler_name = 'command_%s' % cmd
            if hasattr(self, handler_name):
                return getattr(self, handler_name)(cmd, cmd_data)

    def send_room(self, data, type=None):
        if self.ws_connected:
            self.emit('room', {'type': type, 'data': data})

    def command_discover(self, cmd, data):
        """answer discover request"""
        #self.send_room({ 'type': 'jitsi', 'id': self.worker_id }, 'discover')
        self.send_update();

    def command_connect(self, cmd, data):
        self.connect_room(data['room'])

    def command_reconnect(self, cmd, data):
        self.connect_room(self.jitsi_room)

    def command_disconnect(self, cmd, data):
        self.stop_jitsi()
        self.status = "disconnected"
        self.jitsi_room = None
        self.send_update();

    def command_getParticipants(self, cmd, data):
        if self.jitsi_connected:
            self.jitsi.getParticipants()

    def command_toggleTileView(self, cmd, data):
        if self.jitsi_connected:
            self.jitsi.toggleTileView()

    def command_showParticipant(self, cmd, data):
        if self.jitsi_connected:
            self.jitsi.showParticipant(data['id'])

    def command_setParticipantVisible(self, cmd, data):
        if self.jitsi_connected != True:
            return
        if 'visible' in data and data['visible'] == False:
            visible = False
        else:
            visible = True
        log.info("seting %s visible %s" % (data['id'], visible))
        self.jitsi.setParticipantVisible(data['id'], visible)

    def command_setParticipantVolumeMute(self, cmd, data):
        if self.jitsi_connected != True:
            return
        volume = None
        mute = None
        if 'volume' in data:
            volume = data['volume']
        if 'mute' in data:
            mute = data['mute']
        log.info(f"setting participant {data['id']} volume {volume}, mute: {mute}")
        self.jitsi.setParticipantVolumeMute(data['id'], volume, mute)

    def command_toggleParticipantMute(self, cmd, data):
        if self.jitsi_connected != True:
            return
        log.info(f"toggling audio mute of { data['id']}")
        self.jitsi.toggleParticipantMute(data['id'])


    def connect_room(self, room):
        self.status = "connecting"
        self.send_update();
        self.launch(room)
        self.hide_ui_elements()
        if self.options.get('backgroundimage'):
            self.jitsi.setBackgroundImageUrl(self.options.get('backgroundimage'))
        self.status = "connected"
        self.start_tickers()


    def send_update(self):
        data = {
            'id':           self.worker_id,
            'status':       self.status,
            'room:':        self.jitsi_room,
            'participants': self.jitsi.getParticipants() if self.jitsi_connected else []
        }
        self.send_room(data, 'jitsi')

    def start_tickers(self):
        sio.start_background_task(self.task_send_update)

    def task_send_update(self):
        while self.jitsi_connected:
            self.send_update()
            sio.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='RemoeStudio Jitsi WebSocket Display Drone')
    # jitsi options
    parser.add_argument('--url', help='Jitsi Server Url', type=str, default=env.get('URL', 'http://jitsi.meet/'))
    parser.add_argument('--nick', help='Jitsi Display Name', type=str, default=env.get('NICK', 'Jitsi-Client'))
    parser.add_argument('--xmpplogin', help='XMPP Login', type=str, default=env.get('XMPPLOGIN'))
    parser.add_argument('--xmpppass', help='XMPP Password', type=str, default=env.get('XMPPPASS'))

    # websocket options
    parser.add_argument('--ws', help='WebSocket URL', type=str, default=env.get('WS', "http://localhost:5000"))
    parser.add_argument('--wsroom', help='WebSocket Room', type=str, default=env.get('WSROOM', "room"))
    parser.add_argument('--wsnamespace', help='WebSocket Namespace', type=str, default=env.get('WSNAMESPACE', "/regie"))
    parser.add_argument('--wsworker', help='WebSocket Worker ID', type=str, default=env.get('WSWORKER', "jitsi"))

    # display options etc.
    parser.add_argument('--bgurl', help='Background image URL', type=str, default=env.get('BGURL'))
    args = parser.parse_args()

    sio.connect(args.ws, namespaces=[args.wsnamespace])

    display = JitsiNamespace(args.wsnamespace, args.wsroom,
                jitsi_url   = args.url,
                jitsi_email = None,
                displayname = args.nick,
                xmpp_login = args.xmpplogin,
                xmpp_password = args.xmpppass,
                worker_id = args.wsworker,
                backgroundimage = args.bgurl
            )

    signal.signal(signal.SIGTERM, display.quit)
    sio.register_namespace(display)
    sio.wait()


if __name__ == '__main__':
    exit(main())
