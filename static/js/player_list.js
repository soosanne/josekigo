Vue.component('playerlist', {
	components: {
	},
	template: `
		<div class="list-group">
		    <div v-for="player in this.players" class="list-group-item list-group-item-action">
    		    <div @click="open_page('https://soosanne.pythonanywhere.com/player/' + player.player_uuid)">
    		        <span class="lead font-weight-bold"><strong>{{ player.player_name }}</strong></span>
    		    </div>
		    </div>
		</div>
	`,
	data: function() {
		return {
            players: [],
            editing_item: 0,
		}
	},
	methods: {
	    get_data: function() {
	        // Don't update data if we're in the middle of editing. That could be very annoying
	        if(this.editing_item == 0) {
                // Modify API URL to show_inactive if the checkbox it checked
	            url = 'https://soosanne.pythonanywhere.com/api/players';

	            // Get data from the API. This automatically updates the view.
    			axios.get(url).then(response => {
    			    this.players = response.data;
    			});
	        }
	    },
	    open_page: function(location) {
	        window.location.href = location;
	    },
	},
	mounted: function() {
		this.get_data();
	}
});
