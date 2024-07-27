<script setup >
import { RouterView } from 'vue-router'
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
const store = DashboardConfigurationStore();
</script>

<template>
	<nav class="navbar bg-dark sticky-top" data-bs-theme="dark">
		<div class="container-fluid">
			<span class="navbar-brand mb-0 h1">WGDashboard</span>
		</div>
	</nav>
	<Suspense>
		<RouterView v-slot="{ Component }">
			<Transition name="fade2" mode="out-in">
				<Component :is="Component"></Component>
			</Transition>
		</RouterView>
	</Suspense>
</template>

<style scoped>
.app-enter-active,
.app-leave-active {
	transition: all 0.3s ease-in-out;
	/*position: absolute;*/
	/*padding-top: 50px*/
}

.app-enter-from,
.app-leave-to {
	transform: translateX(-30px);
	opacity: 0;
}
</style>