<script setup>
import { RouterView } from 'vue-router'
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {watch} from "vue";
const store = DashboardConfigurationStore();
store.initCrossServerConfiguration();

watch(store.CrossServerConfiguration, () => {
	store.syncCrossServerConfiguration()
}, {
	deep: true
});


</script>

<template>
	<nav class="navbar bg-dark sticky-top" data-bs-theme="dark">
		<div class="container-fluid d-flex text-body">
			<span class="navbar-brand mb-0 h1">WGDashboard</span>
			<span class="ms-auto" v-if="store.getActiveCrossServer() !== undefined">
				<i class="bi bi-server me-2"></i>{{store.getActiveCrossServer().host}}
			</span>
		</div>
	</nav>
	<Suspense>
		<RouterView v-slot="{ Component }">
			<Transition name="app" mode="out-in">
				<Component :is="Component"></Component>
			</Transition>
		</RouterView>
	</Suspense>
</template>

<style scoped>
.app-enter-active,
.app-leave-active {
	transition: all 0.3s cubic-bezier(0.82, 0.58, 0.17, 0.9);
}

.app-enter-from{
	transform: translateY(20px);
	opacity: 0;
}

.app-leave-to {
	transform: translateY(-20px);
	opacity: 0;
}
</style>