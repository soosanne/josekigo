Vue.component('tournamentgamelist', {
	components: {
	},
	template: `
    <div>
        <div>
            <span v-if="uuid != ''" style="margin-left: 15px;">Wins: {{count_wins}} - Losses {{totalmatches - count_wins}} - Total games: {{totalmatches}}</span>
            <span v-else style="margin-left: 15px;">Total games: {{totalmatches}}</span>
        </div>
        <div class="gamelist-buttons">
    	    <span>
        	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="select_page(0)"><<</span>
        	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="next_page(-1)"><</span>
                <span v-for="page in this.pagelist">
                    <span v-if="page != -1" class="badge rounded-pill mb-1 pagebuttons" :class="[ (page == pagenumber) ? 'bg-primary':'bg-secondary' ]" @click="select_page(page)">{{page+1}}</span>
                    <span v-else class="mb-1 dotdot">..</span>
                </span>
        	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="next_page(1)">></span>
        	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="select_page(totalpages-1)">>></span>
    	    </span>

    	    <span>
                <span class="badge rounded-pill mb-1 pagebuttons" @click="set_boardsize_filter(0);" :class="[ (boardsize == 0) ? 'bg-primary':'bg-secondary' ]" >all</span>
                <span v-if="gamecount19 > 0" class="badge rounded-pill mb-1 pagebuttons" @click="set_boardsize_filter(19);" :class="[ (boardsize == 19) ? 'bg-primary':'bg-secondary' ]">19x19</span>
                <span v-if="gamecount13 > 0" class="badge rounded-pill mb-1 pagebuttons" @click="set_boardsize_filter(13);" :class="[ (boardsize == 13) ? 'bg-primary':'bg-secondary' ]">13x13</span>
                <span v-if="gamecount9 > 0" class="badge rounded-pill mb-1 pagebuttons" @click="set_boardsize_filter(9);" :class="[ (boardsize == 9) ? 'bg-primary':'bg-secondary' ]">9x9</span>
            </span>

            <span>
                <span class="badge rounded-pill mb-1 pagebuttons" :class="[ (view=='grid') ? 'bg-primary':'bg-secondary' ]" @click="change_view('grid')">
                    <svg fill="white" width="16" height="16" viewBox="0 0 250 250">
                      <rect class="square" x="10" y="10" width="75" height="75" /><rect class="square" x="95" y="10" width="75" height="75" /><rect class="square" x="180" y="10" width="75" height="75" />
                      <rect class="square" x="10" y="95" width="75" height="75" /><rect class="square" x="95" y="95" width="75" height="75" /><rect class="square" x="180" y="95" width="75" height="75" />
                      <rect class="square" x="10" y="180" width="75" height="75" /><rect class="square" x="95" y="180" width="75" height="75" /><rect class="square" x="180" y="180" width="75" height="75" />
                    </svg>
                </span>

                <span class="badge rounded-pill mb-1 pagebuttons" :class="[ (view=='list') ? 'bg-primary':'bg-secondary' ]" @click="change_view('list')">
                    <svg fill="white" width="16" height="16" viewBox="0 0 250 250">
                      <rect class="square" x="10" y="10" width="245" height="75" /><rect class="square" x="10" y="95" width="245" height="75" /><rect class="square" x="10" y="180" width="245" height="75" />
                    </svg>
                </span>
            </span>
        </div>
        <div v-if="view=='grid'" class="container">
            <div class="row row-cols-auto">
                <gamecard v-for="game in this.view_games"
                    :game="game"
                    :whiteplayer_name="lookup_name(game.game_whiteplayer)" :blackplayer_name="lookup_name(game.game_blackplayer)"
                    :timeago="time_ago(game.game_datetime)" :tournament_name="lookup_tournament(game.game_tournament)" />
            </div>
        </div>
        <table v-if="view=='list'" class="table">
            <thead>
                <tr>
                    <th>When</th>
                    <th>Players</th>
                    <th>Result</th>
                    <th colspan="3">
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="game in this.view_games">
                    <td class="list-timeago">
                        {{ time_ago(game.game_datetime) }}
                    </td>
                    <td class="list-players">
                        <span style="white-space: nowrap;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-circle-fill" viewBox="0 0 16 16">
                                <circle r="7" cx="8" cy="8" stroke="black" fill="white" stroke-width="1" />
                            </svg>
                            <a :href="'https://soosanne.pythonanywhere.com/player/' + game.game_whiteplayer">
                                {{ lookup_name(game.game_whiteplayer) }}
                            </a>
                        </span>
                        vs
                        <span style="white-space: nowrap;">
                            <a :href="'https://soosanne.pythonanywhere.com/player/' + game.game_blackplayer">
                                {{ lookup_name(game.game_blackplayer) }}
                            </a>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-circle-fill" viewBox="0 0 16 16">
                                <circle r="7" cx="8" cy="8" stroke="white" fill="black" stroke-width="1" />
                            </svg>
                        </span>
                    </td>
                    <td class="list-result">
                        {{ lookup_name(game.game_winner) }}, {{ game.game_score }}
                    </td>
                    <td class="list-settings">
                        {{ game.game_boardsize }}x{{ game.game_boardsize }}, {{ game.game_handicap }} handicap, {{ game.game_komi }} komi
                    </td>
                    <td class="list-tournament">
                        <span v-if="game.game_tournament" class="badge bg-secondary rounded-pill py-2">
                            <a :href="'https://soosanne.pythonanywhere.com/tournament/' + game.game_tournament" class="link-light text-decoration-none">
                                {{ lookup_tournament(game.game_tournament) }}<span v-if="game.game_tournamentround"> - Round {{ game.game_tournamentround }}</span>
                            </a>
                        </span>
                        <span v-if="editing_item == game.game_id">
                            <select v-model="game.game_tournamentround">
                                <option v-for="round in rounds" :value="round">{{ round }}</option>
                            </select>
                            <a @click="edit_data(game)" class="link-light text-decoration-none badge rounded-pill py-2 bg-secondary pagebuttons">set</a>
                        </span>
                        <a v-if="admin && editing_item == 0" @click="editing_item=game.game_id" class="link-light text-decoration-none badge rounded-pill py-2 bg-secondary pagebuttons">edit</a>
                        <a v-if="editing_item == game.game_id" @click="editing_item=0" class="link-light text-decoration-none badge rounded-pill py-2 bg-secondary pagebuttons">cancel</a>
                    </td>
                    <td class="list-viewgame">
                        <span class="badge bg-primary rounded-pill py-2">
                            <a class="link-light text-decoration-none" :href="'https://soosanne.pythonanywhere.com/game/' + game.game_id">view game</a>
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
	    <div>
    	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="select_page(0)"><<</span>
    	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="next_page(-1)"><</span>
            <span v-for="page in this.pagelist">
                <span v-if="page != -1" class="badge rounded-pill mb-1 pagebuttons" :class="[ (page == pagenumber) ? 'bg-primary':'bg-secondary' ]" @click="select_page(page)">{{page+1}}</span>
                <span v-else class="mb-1 dotdot">..</span>
            </span>
    	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="next_page(1)">></span>
    	    <span class="badge rounded-pill mb-1 pagebuttons bg-secondary" @click="select_page(totalpages-1)">>></span>
	    </div>
    </div>
	`,
	data: function() {
		return {
            updateInterval: 60000, // 60 seconds
            view: "grid",
            tournaments: [],
            players: [],
            games: [],
            view_games: [],
            editing_item: 0,
            boardsize: 0,
            pagelist: [0],
            pagenumber: 0,
            totalmatches: 0,
            totalpages: 0,
            count_wins: 0,
            rounds: [1,2,3,4,5],
            selectedvalue: 1,
            gamecount19: 0,
            gamecount13: 0,
            gamecount9: 0,
		}
	},
	props: {
        uuid: {
            type: String,
            default: ''
        },
        tournament: {
            type: Number,
            default: 0
        },
        admin: {
            type: Boolean,
            default: false
        },
        pagesize: {
            type: Number,
            default: 20
        }
    },
	methods: {
	    get_players: function() {
            url = 'https://soosanne.pythonanywhere.com/api/players';
			axios.get(url).then(response => {
                const d = {};

			    for (const p of response.data) {
                    d[p.player_uuid] = p.player_name;
                }

			    this.players = d;
			});
	    },
	    get_tournaments: function() {
            url = 'https://soosanne.pythonanywhere.com/api/tournaments';
			axios.get(url).then(response => {
                const d = {};

			    for (const p of response.data) {
                    d[p.tournament_id] = p.tournament_name;
                }

			    this.tournaments = d;
			});
	    },
	    get_games: function() {
	        // Don't update data if we're in the middle of editing. That could be very annoying
	        if(this.editing_item == 0) {
	            url = 'https://soosanne.pythonanywhere.com/api/games';

                if(this.uuid != '') {
	                url = url + "/" + this.uuid;
                } else if(this.tournament != 0) {
                    url = url + "/tournament/" + this.tournament;
                }

	            // Get data from the API. This automatically updates the view.
    			axios.get(url).then(response => {
    			    this.games = response.data;
    			    this.filter_games();
    			});
	        }

	    },
	    lookup_name: function(name) {
	        return(this.players[name]);
	    },
	    lookup_tournament: function(tournament) {
	        return(this.tournaments[tournament]);
	    },
	    open_page: function(location) {
	        window.location.href = location;
	    },
	    edit_data: function(game) {
	        // Call the API with the payload to update the database
	        axios.post('https://soosanne.pythonanywhere.com/api/game/' + game.game_id + "/round/" + game.game_tournamentround)
	        .then(response => {
	            this.get_games();
	            this.filter_games();
	        })
	        .catch(function (error) {
	            this.get_games();
	            this.filter_games();
            });

            this.editing_item = 0;
	    },
		time_ago: function (date1) {
	 		var date1InMillis = Date.parse(date1);
		  	var date2InMillis = Date.now();

			offset = new Date().getTimezoneOffset();

		  	var seconds = 1000;
		  	var minutes = seconds * 60;
		  	var hours = minutes * 60;
		  	var days = hours * 24;

			var seconds_between = Math.round(Math.abs(date1InMillis - date2InMillis) / seconds) + (offset * 60);

			days = 0;
			if(seconds_between > 86400) {
			    days = Math.round(seconds_between / 86400)
			}

			if (seconds_between <= 5)
				return "just now";

            if(days > 0) {
                if(days > 730) {
                    return(~~(days / 365) + " years ago")
                } else if(days > 365) {
                    return("1 year ago")
                } else if(days > 60) {
                    return(~~(days / 30) + " months ago")
                } else if (days > 30) {
                    return("1 month ago")
                } else if (days > 13) {
                    return(~~(days / 7) + " weeks ago")
                } else if (days > 2) {
                    return(days + " days ago")
                } else {
                    return(24 + ~~(seconds_between / 3600) + " hours ago")
                }
            } else {
                if(seconds_between > 7200) {
                    return(~~(seconds_between / 3600) + " hours ago")
                } else if (seconds_between > 3600) {
                    return("1 hour ago")
                } else if (seconds_between > 120) {
                    return(~~(seconds_between / 60) + " minutes ago")
                } else if (seconds_between > 60) {
                    return("1 minute ago")
                } else {
                    return(seconds_between + " seconds ago")
                }
            }
		},
        filter_games: function() {
            count_matched = 0;
            count_added = 0;
            this.count_wins = 0;
	        this.view_games = [];
	        this.gamecount19 = 0;
	        this.gamecount13 = 0;
	        this.gamecount9 = 0;

	        // Iterate all games setting up pagination and various variables we use to display and filter the game data
	        for (g of this.games) {
	            // Count games by board size
	            if(g.game_boardsize == 19) {
	                this.gamecount19 += 1;
	            } else if(g.game_boardsize == 13) {
	                this.gamecount13 += 1;
	            } else if(g.game_boardsize == 9) {
	                this.gamecount9 += 1;
	            }

                // Count winning games
                if(g.game_winner == this.uuid) {
                    this.count_wins += 1;
                }

                // Pagination
	            if(this.boardsize == 0 || g.game_boardsize == this.boardsize) {
	                count_matched += 1;
	                if(count_matched > this.pagenumber * this.pagesize) {
                        if(count_added < this.pagesize) {
                            this.view_games.push(g);
            	            count_added += 1;
                        }
                    }
	            }
	        }

            // Set up som variables we use in pagination
	        this.totalmatches = count_matched;
	        this.totalpages = ~~(this.totalmatches / this.pagesize) + 1

            // Set up the pagination buttons
            this.pagelist = [];
	        if(this.totalpages < 10) {
	            for (const x of Array(this.totalpages).keys()) {
	                this.pagelist.push(x);
	            }
	        } else {

	            if(this.pagenumber <= 4) {
    	            for (const x of Array(this.pagenumber+3).keys()) {
    	                this.pagelist.push(x);
    	            }

                    this.pagelist = this.pagelist.concat([
                        -1, this.totalpages - 3, this.totalpages - 2, this.totalpages - 1
                    ]);

	            } else if(this.pagenumber >= this.totalpages - 5) {
	                // Page number is in the first or last few
                    this.pagelist = [0, 1, 2, -1];

    	            for (const x of Array(this.totalpages - (this.pagenumber - 2)).keys()) {
    	                this.pagelist.push(x + this.pagenumber - 2);
    	            }


	            } else {
	                // page number is somewhere in the middle
                    this.pagelist = [
                        0, 1, 2,
                        -1,
                        this.pagenumber - 1, this.pagenumber, this.pagenumber + 1,
                        -1,
                        this.totalpages - 3, this.totalpages - 2, this.totalpages - 1
                    ];
	            }
	        }
		},
		set_boardsize_filter: function(size) {
		    this.boardsize=size;
		    this.filter_games();
		},
		select_page: function(page) {
		    if(page==-1) {
		        return;
		    }
		    this.pagenumber = page;
		    this.filter_games();
		},
		next_page: function(increment) {
		    this.pagenumber += increment;
		    if(this.pagenumber < 0) {
		        this.pagenumber = 0;
		    } else if(this.pagenumber > this.totalpages-1) {
		        this.pagenumber = this.totalpages-1;
		    }
		    this.filter_games();
		},
		change_view: function(view_style) {
		    this.view = view_style;

            const date = new Date();
            date.setTime(date.getTime() + 365 * 24 * 60 * 60 * 1000); // Add 1 year in milliseconds
            const expiresString = date.toUTCString();

            document.cookie = `view=${view_style}; expires=${expiresString}; path=/`;
		},
	},
	computed: {
	},
	mounted: function() {
	    this.get_players();
	    this.get_tournaments();
		this.get_games();
        setInterval(this.get_games, this.updateInterval);
        if(document.cookie.includes('view=')) {
            this.view = document.cookie.split('; ').find(c => c.startsWith('view=')).split('=')[1]
        }
	}
});
