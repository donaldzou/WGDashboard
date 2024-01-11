<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";

export default {
	name: "configurationList",
	async setup(){
		const store = wgdashboardStore();
		await store.getWireguardConfigurations();
		return {store}
	}
}
</script>

<template>
	<div class="mt-4">
		<h3 class="mb-3 text-body">Wireguard Configurations</h3>
		<p class="text-muted" v-if="this.store.WireguardConfigurations.length === 0">You don't have any WireGuard configurations yet. Please check the configuration folder or change it in "Settings". By default the folder is "/etc/wireguard".</p>
		
		<div class="card conf_card rounded-3 shadow" v-else v-for="c in this.store.WireguardConfigurations" :key="c.Name">
			<div class="card-body">
				<div class="row">
					<div class="row">
						<div class="col card-col">
							<small class="text-muted"><strong>CONFIGURATION</strong></small>
							<h6 class="card-title" style="margin:0 !important;"><samp>{{c.Name}}</samp></h6>
						</div>
						<div class="col card-col">
							<small class="text-muted"><strong>STATUS</strong></small>
							<h6><span>{{c.Status ? "Running":"Stopped"}}</span>
								<span class="dot" :class="{active: c.Status}"></span></h6>
						</div>
						<div class="col-sm card-col">
							<small class="text-muted"><strong>PUBLIC KEY</strong></small>
							<h6 style="margin:0 !important;"><samp>{{c.PublicKey}}</samp></h6>
						</div>
						<div class="col-sm index-switch">
							<div class="switch-test">
								<input type="checkbox" class="toggle--switch" checked :id="c.Name + '-switch'">
								<label :for="c.Name + '-switch'" class="toggleLabel"></label>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>