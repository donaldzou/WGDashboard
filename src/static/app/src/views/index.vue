<script>
import Navbar from "@/components/navbar.vue";
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurations} from "@/models/WireguardConfigurations.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export default {
	name: "index",
	components: {Navbar},
	async setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore()
		return {dashboardConfigurationStore}
	}
}
</script>

<template>
	<div class="container-fluid flex-grow-1 main" :data-bs-theme="this.dashboardConfigurationStore.Configuration.Server.dashboard_theme">
		<div class="row h-100">
			<Navbar></Navbar>
			<main class="col-md-9 ml-sm-auto col-lg-10 px-md-4 overflow-y-scroll mb-0"  style="height: calc(100vh - 50px)">
				<Suspense>
					<RouterView v-slot="{Component}">
						<Transition name="fade2" mode="out-in">
							<Component :is="Component"></Component>
						</Transition>
					</RouterView>
				</Suspense>
			</main>
		</div>
	</div>
</template>

<style scoped>

</style>