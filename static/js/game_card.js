Vue.component('gamecard', {
	template: `
        <div class="col card" @click="open_page('https://soosanne.pythonanywhere.com/game/' + game.game_id)">
            <div class="card-topline">
                <div class="card-timeago">
                    {{ timeago }}
                </div>
                <div class="card-tournament">
                    <a :href="'https://soosanne.pythonanywhere.com/tournament/' + game.game_tournament">
                        {{ tournament_name }}<span v-if="game.game_tournamentround"> Round {{game.game_tournamentround}}</span>
                    </a>
                </div>
            </div>
            <div class="card-whitehalf">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-circle-fill player-color" viewBox="0 0 16 16">
                    <circle r="7" cx="8" cy="8" stroke="black" fill="white" stroke-width="1" />
                </svg>
                <a :href="'https://soosanne.pythonanywhere.com/player/' + game.game_whiteplayer">
                    {{ whiteplayer_name }}
                </a>
                <span v-if="game.game_winner == game.game_whiteplayer" class="card-score">
                    <span class="grey-grad">&nbsp;</span><span class="grey-back">
                        {{ game.game_score }}
                        <svg fill="white" width="16" height="16" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>
                    </span>
                </span>
                <span v-else class="card-score"><span class="grey-grad">&nbsp;</span><span class="grey-back">&nbsp;</span></span>
            </div>
            <div class="card-blackhalf">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-circle-fill player-color" viewBox="0 0 16 16">
                    <circle r="7" cx="8" cy="8" stroke="white" fill="black" stroke-width="1" />
                </svg>
                <a :href="'https://soosanne.pythonanywhere.com/player/' + game.game_blackplayer">
                    {{ blackplayer_name }}
                </a>
                <span v-if="game.game_winner == game.game_blackplayer" class="card-score">
                    <span class="grey-grad">&nbsp;</span><span class="grey-back">
                        {{ game.game_score }}
                        <svg fill="white" width="16" height="16" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/></svg>
                    </span>
                </span>
                <span v-else class="card-score"><span class="grey-grad">&nbsp;</span><span class="grey-back">&nbsp;</span></span>
            </div>
            <div class="card-bottom">
                <span>
                    {{ game.game_handicap }} handicap, {{ game.game_komi }} komi
                </span>
                <span>
                    {{game.game_boardsize}}x{{game.game_boardsize}}
                </span>
            </div>
        </div>
	`,
	data: function() {
		return {
		}
	},
	props: {
        game: {
            type: Object,
            required: true,
        },
        whiteplayer_name: {
            type: String,
            default: "white",
        },
        blackplayer_name: {
            type: String,
            default: "black",
        },
        timeago: {
            type: String,
            default: "unknown",
        },
        tournament_name: {
            type: String,
            default: "",
        },
    },
    methods: {
	    open_page: function(location) {
	        window.location.href = location;
	    },
    },
	computed: {
	}
});