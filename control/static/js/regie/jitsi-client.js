Vue.component('jitsi-client', {
  props: ['jitsi'],
  methods: {
    showParticipant: function(participant) {
      console.log("showing", participant.displayName);
      //socket.emit('room', {command: 'showParticipant', data: { id: participant.id }});
      this.$emit('jitsi-event', 'showParticipant', { id: participant.id });
    },
    toggleParticipantMute: function(participant) {
      console.log("mute toggle", participant.displayName);
      //socket.emit('room', {command: 'toggleParticipantMute', data: { id: participant.id }});
      this.$emit('jitsi-event', 'toggleParticipantMute', { id: participant.id });
    },
    toggleParticipantVisible: function(participant) {
      console.log("visible toggle", participant.displayName, !participant.element_visible);
      //socket.emit('room', {command: 'setParticipantVisible', data: { id: participant.id, visible: !participant.element_visible }});
      this.$emit('jitsi-event', 'setParticipantVisible', { id: participant.id, visible: !participant.element_visible });
    },
    setParticipantVolume: function(participant, volume) {
      volume = parseFloat(volume);
      console.log("set volume", volume, participant.displayName);
      //socket.emit('room', {command: 'setParticipantVolumeMute', data: { id: participant.id, volume: volume }});
      this.$emit('jitsi-event', 'setParticipantVolumeMute', { id: participant.id, volume: volume });
    },
    setParticipantVolumeEvent: function(participant, event) {
      this.setParticipantVolume(participant, event.target.value);
    },
    UIconnect: function() {
      if ( this.jitsi.status =! 'disconnected' ) {
        console.error("can not connect jitsi");
      }
      var room = prompt('Jitsi Room Name:');
      if ( room =! null && room != "" ) {
        this.$emit('jitsi-event', 'connect', { room: room } );
      }
    },
    UIdisconnect: function() {
      var confirm = prompt('please enter the word \'DISCONNECT\':');
      if (confirm === "DISCONNECT") {
        this.$emit('jitsi-event', 'disconnect', {} );
      }
    }
  },
  template: `
          <div class="p-3 controlpanel">
          <h5>Jitsi {{ jitsi.id }} status: {{ jitsi.status }}
            <div class="float-right">
              <button type="button" class="btn btn-sm btn-success" v-show="jitsi.status != 'connected'" v-on:click="UIconnect">Connect <i class="fas fa-grip-horizontal"></button>
              <button type="button" class="btn btn-sm btn-danger" v-show="jitsi.status != 'disconnected'" v-on:click="UIdisconnect">Disconnect <i class="fas fa-grip-horizontal"></button>
            </div>
          </h5>
<!--            <button type="button" class="btn btn-secondary">Cut to this cam</button>
            <button type="button" class="btn btn-secondary">Fade to this cam</button> -->

            <table class="table table-striped small jitsi-participants" style="color: white">
                <tbody>
                    <tr>
                        <th>Name</th>
                        <th><i class="fas fa-grip-horizontal"></i></th>
                        <th>Tracks</th>
                        <th>Volume</th>
                        <th>role</th>
                        <th>status</th>
                    </tr>
                    <tr v-for="participant in jitsi.participants" :key="participant.id">
                        <td style="text-align: left">
                            <a v-if="true" v-on:click="showParticipant(participant)" style="cursor: pointer">
                                <i v-for="t in participant.tracks"
                                    v-if="t.type == 'audio' && t.muted != true"
                                    v-bind:style="{ opacity: t.audioLevel*500 + '%' }"
                                    style="color: #60ff80; transition:opacity 0.3s; width:0px;overflow:visible"
                                class="fas fa-circle"></i>
                                <b style="padding-left: 1em">{{ participant.displayName }}</b>
                            </a>
                        </td>
                        <td>
                            <i v-bind:class="{ 'fa-eye': participant.element_visible == true, 'fa-eye-slash': participant.element_visible == false }"
                                class="fas participant-visible" v-on:click="toggleParticipantVisible(participant)" style="cursor: pointer; color: #8af">&nbsp;</i>
                        </td>
                        <td>
                            <i v-for="t in participant.tracks"
                                v-bind:class="{ 'fa-microphone': t.muted == false, 'fa-microphone-slash': t.muted == true, }"
                                v-show="t.type == 'audio'" class="fas">&nbsp;</i>
                            <i v-for="t in participant.tracks"
                                v-bind:class="{ 'fa-video': t.videoType == 'camera', 'fa-desktop': t.videoType == 'desktop' }"
                                v-show="t.muted != true && t.type == 'video'" class="fas">&nbsp;</i>
                        </td>
                        <td style="max-width: 8em">
                            <div style="input-group" v-for="t in participant.tracks" v-if="t.type == 'audio'">
                                <span class="input-group-text" style="padding: .15rem .4rem; background-color: rgba(200,200,200, 0.3); color: white; border: none">
                                    <i v-bind:class="{ 'fa-volume-mute': t.audio_muted == true, 'fa-volume-down': t.audio_muted == false }"
                                        class="fas" v-on:click="toggleParticipantMute(participant)" style="cursor: pointer; color: #8af">&nbsp;</i>
                                    <input type="range" class="custom-range"  min="-40" max="0" step="1" :value="t.audio_volume"
                                        :disabled="t.audio_muted" v-on:input="setParticipantVolumeEvent(participant, $event)">
                                </span>
                            </div>
                        </td>
                        <td>{{ participant.role }}</td>
                        <td>{{ participant.connectionStatus }}</td>
                    </tr>
                </tbody>
            </table>
          <div role="group" aria-label="cut-action">
            <button type="button" class="btn btn-sm btn-secondary" v-show="jitsi.status == 'connected'" v-on:click="$emit('jitsi-event', 'toggleTileView', {})">Toggle Tile View <i class="fas fa-grip-horizontal"></button>
          </div>
        </div>
  `
});
