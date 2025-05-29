import {createRouter, createWebHashHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
	history: createWebHashHistory(),
	routes: [
		{
			path: '/',
			name: 'Home',
			component: HomeView,
		}
	],
})

router.beforeEach((to, from, next) => {
	document.title = to.name + ' | WGDashboard Client'
})

export default router
