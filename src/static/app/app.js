const { createApp, ref } = Vue;
import Index from './index.js'
import Signin from './signin/signin.js'
const {createPinia} = Pinia
import {cookie} from "./cookie.js";

const app = createApp({
	template: `
		<nav class="navbar bg-dark fixed-top" data-bs-theme="dark">
			  <div class="container-fluid">
			        <span class="navbar-brand mb-0 h1">WGDashboard</span>
			  </div>
		</nav>
		<RouterView></RouterView>
	`
});
const pinia = createPinia()
const routes = [
	{
		path: '/', 
		component: Index,
		meta: {
			requiresAuth: true
		}
	},
	{
		path: '/signin', component: Signin
	}
]

const router = VueRouter.createRouter({
	// 4. Provide the history implementation to use. We are using the hash history for simplicity here.
	history: VueRouter.createWebHashHistory(),
	routes, // short for `routes: routes`
});

router.beforeEach((to, from, next) => {
	if (to.meta.requiresAuth){
		if (cookie.getCookie("auth")){
			next()
		}else{
			next("/signin")
		}
	}else {
		next();
	}
});

app.use(router);
app.use(pinia)
app.mount('#app');