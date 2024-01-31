<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";

export default {
	name: "configurationList",
	async setup(){
		const wireguardConfigurationsStore = WireguardConfigurationsStore();
		await wireguardConfigurationsStore.getConfigurations();
		return {wireguardConfigurationsStore}
	}
}
</script>

<template>
	<div class="mt-4">
		<div class="container">
			<div class="d-flex mb-4 ">
				<h3 class="text-body">Wireguard Configurations</h3>
				<RouterLink to="/new_configuration" class="btn btn-dark btn-brand rounded-3 px-3 py-2 shadow ms-auto rounded-3">
					Configuration
					<i class="bi bi-plus-circle-fill ms-2"></i>
				</RouterLink>
			</div>
			<p class="text-muted" v-if="this.wireguardConfigurationsStore.Configurations.length === 0">You don't have any WireGuard configurations yet. Please check the configuration folder or change it in "Settings". By default the folder is "/etc/wireguard".</p>

			<div class="d-flex gap-3 flex-column" v-else >
				<RouterLink :to="'/configuration/' + c.Name"
				            class="card conf_card rounded-3 shadow text-decoration-none" v-for="c in this.wireguardConfigurationsStore.Configurations" :key="c.Name">
					<div class="card-body d-flex align-items-center gap-3 flex-wrap">
						<h6 class="mb-0"><span class="dot" :class="{active: c.Status}"></span></h6>
						<h6 class="card-title mb-0"><samp>{{c.Name}}</samp></h6>
						<h6 class="mb-0 ms-auto">
							<i class="bi bi-chevron-right"></i>
						</h6>
					</div>
					<div class="card-footer">
						<small class="me-2 text-muted">
							<strong>PUBLIC KEY</strong>
						</small>
						<small class="mb-0 d-block d-lg-inline-block ">
							<samp style="line-break: anywhere">{{c.PublicKey}}</samp>
						</small>
					</div>
				</RouterLink>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>