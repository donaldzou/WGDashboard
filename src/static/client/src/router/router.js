import {createWebHashHistory, createRouter} from "vue-router";
import Index from "@/views/index.vue";
import Signin from "@/views/signin.vue";
import Signup from "@/views/signup.vue";

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
			component: Signin,
			name: "Sign In"
		},
		{
			path: '/signup',
			component: Signup,
			name: "Sign Up"
		}
	]
})

router.afterEach((to, from, next) => {
	document.title = to.name + ' | WGDashboard Client'
})

export default router