import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from "@/router/router.js";
import {createPinia} from "pinia";

import 'bootstrap/dist/js/bootstrap.bundle.js'

createApp(App)
	.use(createPinia())
	.use(router)
	.mount('#app')
