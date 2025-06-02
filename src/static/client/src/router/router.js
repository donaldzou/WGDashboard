import {createWebHashHistory, createRouter} from "vue-router";
import Index from "@/views/index.vue";
import SignIn from "@/views/signin.vue";
import SignUp from "@/views/signup.vue";
import Totp from "@/views/totp.vue";

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: '/',
			component: Index,
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
		},
		{
			path: '/totp',
			component: Totp,
			name: "Verify TOTP"
		}
	]
})

router.afterEach((to, from, next) => {
	document.title = to.name + ' | WGDashboard Client'
})

export default router