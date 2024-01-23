import '../../css/dashboard.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import 'bootstrap-icons/font/bootstrap-icons.css'

import {createApp, markRaw} from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'


const app = createApp(App)
app.use(router)
const pinia = createPinia();

pinia.use(({ store }) => {
	store.$router = markRaw(router)
})

app.use(pinia)


app.mount('#app')
