import {createWebHashHistory, createRouter} from "vue-router";
import Index from "@/views/index.vue";
import SignIn from "@/views/signin.vue";
import SignUp from "@/views/signup.vue";
import axios from "axios";
import {requestURl} from "@/utilities/request.js";
import {clientStore} from "@/stores/clientStore.js";

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: '/',
			component: Index,
			meta: {
				auth: true
			},
			name: "Home"
		},
		{
			path: '/signin',
			component: SignIn,
			name: "Sign In"
		},
		{
			path: '/signup',
			component: SignUp,
			name: "Sign Up"
		}
	]
})

router.beforeEach(async (to, from, next) => {
	if (to.meta.auth){
		await axios.get(requestURl('/client/api/validateAuthentication')).then(res => {
			next()
		}).catch(() => {
			const store = clientStore()
			store.newNotification("Sign in session ended, please sign in again", "warning")
			next('/signin')
		})
	}else{
		next()
	}
})

router.afterEach((to, from, next) => {
	document.title = to.name + ' | WGDashboard Client'
})

export default router