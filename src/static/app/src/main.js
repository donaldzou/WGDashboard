import '../../css/dashboard.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'animate.css/animate.compat.css'
import '@vuepic/vue-datepicker/dist/main.css'

import {createApp, markRaw} from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {fetchGet} from "@/utilities/fetch.js";

let Locale;
await fetch("/api/locale").then(res => res.json()).then(res => Locale = JSON.parse(res.data))


const app = createApp(App)

app.use(router)

const pinia = createPinia();
pinia.use(({ store }) => {
	store.$router = markRaw(router)
})

app.use(pinia)

const store = DashboardConfigurationStore()
window.Locale = Locale;
app.mount('#app')