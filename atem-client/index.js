
config = {
    worker_id: 'atem',
    roomname: process.env.WS_ROOM ||'studio_saal1',
    ws_namespace: '/regie',
    ws_host: process.env.WS_HOST,
    atem_ip: '192.168.42.90'
}

const io = require('socket.io-client')
const { Atem } = require('atem-connection')
const objectPath = require("object-path");

const EventEmitter = require('events');
const AtemEvent = new EventEmitter();
const WsCommand = new EventEmitter();

const sio = io(config.ws_host + config.ws_namespace)

const atem = new Atem()
atem.on('info', console.log)
atem.on('error', console.error)


/**
 * Atem Events
 */

const sendUpdate = function(event) {
    send_room({
        inputs: getVideoInputs(atem.state),
        audio:  getAudioInputs(atem.state),
        state:  getPreviewProgram(atem.state)
    }, 'atem');
};
AtemEvent.on('video.ME.0.previewInput', sendUpdate);
AtemEvent.on('video.ME.0.programInput', sendUpdate);
AtemEvent.on('audio.channels.1', sendUpdate);
AtemEvent.on('audio.channels.2', sendUpdate);
AtemEvent.on('audio.channels.3', sendUpdate);
AtemEvent.on('audio.channels.4', sendUpdate);
AtemEvent.on('audio.channels.5', sendUpdate);
AtemEvent.on('audio.channels.6', sendUpdate);
AtemEvent.on('audio.channels.7', sendUpdate);
AtemEvent.on('audio.channels.8', sendUpdate);
AtemEvent.on('audio.channels.1001', sendUpdate); // XLR


 /* Atem connection logic */
atem.connect(config.atem_ip)

atem.on('connected', () => {
    console.log('atem: connected.');
    setImmediate(() => {
        sendUpdate();
    });
    // send periodical updates
    setInterval(() => {
        sendUpdate();
    }, 10000);
})

atem.on('stateChanged', (state, pathToChange) => {
    // console.log(state, pathToChange); // catch the ATEM state.
    //console.log('stateChanged', pathToChange, atem.state.video);
    for (var path of pathToChange){
        if (path in AtemEvent._events) {
            //console.log("emitting", path, state, objectPath.get(atem.state, path));
            AtemEvent.emit(path, path, state);
        } else if ( path != "info.lastTime" ) {
            console.log('unknown event:', path);
            //console.log(JSON.stringify(state, null, 4));
        }
    }
});

/**
 * Socket.io Events
 */

sio.on('connect', function(){
    console.log('connect');
    sio.emit('register', {'type': 'worker', 'room': config.roomname, 'id': config.worker_id});
});
sio.on('register', function(){
    console.log('registered!');
});
sio.on('disconnect', function(){
    console.log('disconnect');    
});
sio.on('room', function(data){
    console.log('room message:', data);
    if (data.command && data.command in WsCommand._events) {
        if (data.id && data.id != config.worker_id )
            return
        WsCommand.emit(data.command, data.command, data.data);
    }
});


/*
 * WebSocket Commands
 */

WsCommand.on('discover', function(event, data) {
    console.log('answering discover.');
    sendUpdate();
});

WsCommand.on('changeProgramInput', function(event, data) {
    atem.changeProgramInput(data.id).then(() => {
        console.log('Program set.');
    });
});
WsCommand.on('changePreviewInput', function(event, data) {
    atem.changePreviewInput(data.id).then(() => {
        console.log('Preview set.');
    });
});
WsCommand.on('setAuxSource', function(event, data) {
    atem.setAuxSource(data.id).then(() => {
        console.log('Preview set.');
    });
});
WsCommand.on('cut', function(event, data) {
    atem.cut();
});
WsCommand.on('auto', function(event, data) {
    atem.autoTransition();
});

WsCommand.on('setAudioMixerInputGain', function(event, data) {
    atem.setAudioMixerInputGain(data.id, data.gain);
});
WsCommand.on('setAudioMixerMasterGain', function(event, data) {
    atem.setAudioMixerMasterGain(data.gain);
});
WsCommand.on('setAudioMixerInputMixOption', function(event, data) {
    var option = null;
    switch ( data.state ) {
        case 'off': option = 0; break;
        case 'on' : option = 1; break;
        case 'afv': option = 2; break;
    }
    if ( option == null)
        console.error("unknown audio mix option:", data.state);
    else
        atem.setAudioMixerInputMixOption(data.id, option);
});
WsCommand.on('setMediaClip', function(event, data) {
    atem.setMediaClip(data.id, data.name);
});



/*
 * helper functions
 */

function send_room(data, type=null) {
    sio.emit('room', {'type': type, 'data': data})
}

function getPreviewProgram(state) {
    for (let eff of state.video.mixEffects) {
        if (eff.index === 0) {
            return {
                preview: eff.previewInput,
                program: eff.programInput, 
                inTransition: eff.transitionPosition.inTransition
            };
        }
    }
}

function getVideoInputs(state) {
    var inputs = {}
    for (const [key, input] of Object.entries(state.inputs)) {
        if (
            input.externalPortType != 1 &&  // SDI
            input.externalPortType != 2 &&  // HDMI
            input.internalPortType != 4     // MP
        ) continue;
        inputs[key] = {
            id:         input.inputId,
            shortName:  input.shortName,
            longName:   input.longName
        }
    }
    return inputs;
}

function getAudioInputs(state) {
    var channels = {
        channels: {},
        master: {
            gain: state.audio.master.gain
        }
    };
    for (const [key, channel] of Object.entries(state.audio.channels)) {
        var type = null;
        switch(channel.portType){
            case  1: type = 'SDI' ; break;
            case  2: type = 'HDMI'; break;
            case 32: type = 'XLR';  break;
        }
        if ( type == null )
            continue; // ignore other input types
        var mute_state;
        switch(channel.mixOption){
            case 0: mute_state = 'off'; break;
            case 1: mute_state = 'on' ; break;
            case 2: mute_state = 'afv'; break;
        }
        channels.channels[key] = {
            id:     parseInt(key),
            state:  mute_state,
            gain:   channel.gain,
            type:   type
        }
    }
    return channels;
}
