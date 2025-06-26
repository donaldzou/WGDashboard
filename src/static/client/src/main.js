import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router/router.js";
import {createPinia} from "pinia";

import 'bootstrap/dist/js/bootstrap.bundle.js'
import {clientStore} from "@/stores/clientStore.js";

const app = createApp(App)

app.use(createPinia())
const store = clientStore()
await fetch("/client/api/serverInformation").then(res => res.json()).then(res => store.serverInformation = res.data)


app.use(router)
app.mount("#app")