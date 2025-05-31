import {createWebHashHistory, createRouter} from "vue-router";
import Index from "@/views/index.vue";

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: '/',
			component: Index,
			name: "Home"
		}
	]
})

router.afterEach((to, from, next) => {
	document.title = to.name + ' | WGDashboard Client'
})

export default router