Vue.component('atem-client', {
    props: ['atem'],
    filters: {
        gainFormat (value) {
            if (value >= 0)
                return "+" + value.toFixed(1);
            return value.toFixed(1);
        }
    },
    methods: {
        AtemProgram: function(id) {
            console.log(id);
        },
        input_isLive: function(id) {
            if ( this.atem.state.program == id )
                return true;
            if ( this.atem.state.preview == id && this.atem.state.inTransition )
                return true;
            return false;
        },
        audio_getName: function(id) {
            if (id in this.atem.inputs)
                return this.atem.inputs[id].longName;
            return this.atem.audio.channels[id].type;
        },
        setAudioInputGain: function(id, gain) {
            this.atem.audio.channels[id].gain = gain;
            this.$emit('atem-event', 'setAudioMixerInputGain', { id: id, gain: gain });
        }
    },
    template: `
      <div class="controlpanel mixer">
        <div class="p-2 mixerinputs mixerinputs-audio">
          <h5>Audio Inputs</h5>
            <div class="btn-group mr-2" role="group" aria-label="Mixer Audio" style="width:100%; background: rgba(255,255,255, 0.05)">
                <div  v-for="i in atem.audio.channels" :key="i.id" class="btn-group" role="group" v-if="audio_getName(i.id) != ''">
                    <button type="button" class="btn" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"
                    v-bind:class="{ 'btn-outline-secondary': i.state == 'off', 'btn-success': i.state == 'on',
                        'btn-outline-warning': i.state == 'afv' && !input_isLive(i.id), 'btn-warning': i.state == 'afv' && input_isLive(i.id)}">
                    {{ audio_getName(i.id) }}
                    </button>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" href="#" v-show=" i.state != 'on'"
                        v-on:click="$emit('atem-event', 'setAudioMixerInputMixOption', { id: i.id, state: 'on' })">ON</a>
                        <a class="dropdown-item" href="#" v-show=" i.state != 'off'"
                        v-on:click="$emit('atem-event', 'setAudioMixerInputMixOption', { id: i.id, state: 'off' })">OFF</a>
                        <a class="dropdown-item" href="#" v-show=" i.state != 'afv'" v-if="i.id in atem.inputs"
                        v-on:click="$emit('atem-event', 'setAudioMixerInputMixOption', { id: i.id, state: 'afv' })">On Video</a>
                        <div class="dropdown-item" style="min-width: 8rem">
                            <span style="cursor:col-resize" v-on:click="setAudioInputGain( i.id, 0)" >{{ i.gain | gainFormat }}</span>
                            <input type="range" class="custom-range"  min="-60" max="6" step="0.2" style="height: 100%; width: auto; vertical-align: middle;"
                            :value="i.gain" v-on:input="setAudioInputGain( i.id, parseFloat($event.target.value))">
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="p-4">
        </div>
        <div class="p-2 mixerinputs mixerinputs-program">
          <h5>Video Mix</h5>
            <div class="btn-group mr-2" role="group" aria-label="Mixer Program" style="width:100%">
                <button type="button" class="btn" style="cursor: no-drop" v-for="i in atem.inputs" :key="i.id"
                 v-bind:class="{ 'btn-secondary': ! input_isLive(i.id), 'btn-danger': input_isLive(i.id) }"
                 v-on:click="$emit('atem-event', 'changeProgramInput', { id: i.id })" v-if="i.longName != ''">
                    {{ i.longName }}
                </button>
            </div>
        </div>
        <div class="p-2 mixerinputs mixerinputs-preview">
            <div class="btn-group mr-2" role="group" aria-label="Mixer Preview" style="width:100%">
                <button type="button" class="btn" v-for="i in atem.inputs" :key="i.id"
                 v-bind:class="{ 'btn-secondary': i.id != atem.state.preview, 'btn-success': i.id == atem.state.preview }"
                 v-on:click="$emit('atem-event', 'changePreviewInput', { id: i.id })" v-if="i.longName != ''">
                    {{ i.longName }}
                </button>
            </div>
        </div>
        <div class="p-4 text-center">
          <div role="group" aria-label="cut-action">
            <button type="button" class="btn btn-lg btn-secondary" v-on:click="$emit('atem-event', 'cut', {})">Cut</button>
            <button type="button" class="btn btn-lg btn-secondary" v-on:click="$emit('atem-event', 'auto', {})"
                v-bind:class="{ 'progress-bar-striped progress-bar-animated active': atem.state && atem.state.inTransition}" >Fade</button>
          </div>
        </div>
      </div>
    `
});
