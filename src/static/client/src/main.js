import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router/router.js";
import {createPinia} from "pinia";

import 'bootstrap/dist/js/bootstrap.bundle.js'
import {clientStore} from "@/stores/clientStore.js";

const app = createApp(App)

app.use(createPinia())



app.use(router)
app.mount("#app")