import Vue from 'vue'
import App from './App'
// import store from './store/index.js'
// import websocket from './store/index.js'
 
// Vue.prototype.$websocket = websocket;

// Vue.prototype.$store = store
Vue.config.productionTip = false

App.mpType = 'app'

const app = new Vue({
    ...App,
	// store,
	// websocket
})
app.$mount()
