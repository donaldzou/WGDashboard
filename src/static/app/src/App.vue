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
			<Transition name="fade" mode="out-in">
				<Component :is="Component"></Component>
			</Transition>
		</RouterView>
	</Suspense>
</template>