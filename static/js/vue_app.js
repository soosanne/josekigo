Vue.config.devtools = true;

var app = new Vue({
	el: '#app',
	components: {
	},
	data: {
        message: "Hello World",
        count: 1
    },
    methods: {
        increment: function() {
            this.count = this.count+1;
        }
    }
});
