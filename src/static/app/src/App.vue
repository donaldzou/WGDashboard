<script setup async>
import { RouterView } from 'vue-router'
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {computed, watch} from "vue";
const store = DashboardConfigurationStore();
store.initCrossServerConfiguration();
if (window.IS_WGDASHBOARD_DESKTOP){
	store.IsElectronApp = true;
	store.CrossServerConfiguration.Enable = true;
}
watch(store.CrossServerConfiguration, () => {
	store.syncCrossServerConfiguration()
}, {
	deep: true
});
const getActiveCrossServer = computed(() => {
	if (store.ActiveServerConfiguration){
		return store.CrossServerConfiguration.ServerList[store.ActiveServerConfiguration]
	}
	return undefined
})
</script>

<template>
	<div style="z-index: 9999; height: 5px" class="position-absolute loadingBar top-0 start-0"></div>
	<nav class="navbar bg-dark sticky-top" data-bs-theme="dark">
		<div class="container-fluid d-flex text-body align-items-center">
			<span class="navbar-brand mb-0 h1">WGDashboard</span>
			<small class="ms-auto text-muted" v-if="getActiveCrossServer !== undefined">
				<i class="bi bi-server me-2"></i>{{getActiveCrossServer.host}}
			</small>
			<a role="button" class="navbarBtn text-body"
			   @click="store.ShowNavBar = !store.ShowNavBar"
			   style="line-height: 0; font-size: 2rem">
				<i class="bi bi-list"></i>
			</a>
		</div>
	</nav>
	<Suspense>
		<RouterView v-slot="{ Component }">
			<Transition name="app" mode="out-in" type="transition" appear>
				<Component :is="Component"></Component>
			</Transition>
		</RouterView>
	</Suspense>
</template>

<style scoped>
.app-enter-active,
.app-leave-active {
	transition: all 0.7s cubic-bezier(0.82, 0.58, 0.17, 1);
}
.app-enter-from,
.app-leave-to{
	opacity: 0;
	transform: scale(1.1);
}
@media screen and (min-width: 768px) {
	.navbar{
		display: none;
	}
}
</style>