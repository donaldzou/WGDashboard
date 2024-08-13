<script>
import {wgdashboardStore} from "@/stores/wgdashboardStore.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import PeersDefaultSettingsInput from "@/components/settingsComponent/peersDefaultSettingsInput.vue";
import {ipV46RegexCheck} from "@/utilities/ipCheck.js";
import AccountSettingsInputUsername from "@/components/settingsComponent/accountSettingsInputUsername.vue";
import AccountSettingsInputPassword from "@/components/settingsComponent/accountSettingsInputPassword.vue";
import DashboardSettingsInputWireguardConfigurationPath
	from "@/components/settingsComponent/dashboardSettingsInputWireguardConfigurationPath.vue";
import DashboardTheme from "@/components/settingsComponent/dashboardTheme.vue";
import DashboardSettingsInputIPAddressAndPort
	from "@/components/settingsComponent/dashboardSettingsInputIPAddressAndPort.vue";
import DashboardAPIKeys from "@/components/settingsComponent/dashboardAPIKeys.vue";
import AccountSettingsMFA from "@/components/settingsComponent/accountSettingsMFA.vue";

export default {
	name: "settings",
	methods: {ipV46RegexCheck},
	components: {
		AccountSettingsMFA,
		DashboardAPIKeys,
		DashboardSettingsInputIPAddressAndPort,
		DashboardTheme,
		DashboardSettingsInputWireguardConfigurationPath,
		AccountSettingsInputPassword, AccountSettingsInputUsername, PeersDefaultSettingsInput},
	setup(){
		const dashboardConfigurationStore = DashboardConfigurationStore()
		return {dashboardConfigurationStore}
	},
	watch: {
		// 'dashboardConfigurationStore.Configuration': {
		// 	deep: true,
		// 	handler(){
		// 		this.dashboardConfigurationStore.updateConfiguration();
		// 	}
		// }
	}
}
</script>

<template>
	<div class="mt-5">
		<div class="container">
			<h3 class="mb-3 text-body">Settings</h3>
			<DashboardTheme></DashboardTheme>
			<div class="card mb-4 shadow rounded-3">
				<p class="card-header">Peers Default Settings</p>
				<div class="card-body">
					<PeersDefaultSettingsInput targetData="peer_global_dns" title="DNS"></PeersDefaultSettingsInput>
					<PeersDefaultSettingsInput targetData="peer_endpoint_allowed_ip" title="Peer Endpoint Allowed IPs"></PeersDefaultSettingsInput>
					<PeersDefaultSettingsInput targetData="peer_mtu" title="MTU (Max Transmission Unit)"></PeersDefaultSettingsInput>
					<PeersDefaultSettingsInput targetData="peer_keep_alive" title="Persistent Keepalive"></PeersDefaultSettingsInput>
					<PeersDefaultSettingsInput targetData="remote_endpoint" title="Peer Remote Endpoint"
					                           :warning="true" warningText="This will be changed globally, and will be apply to all peer's QR code and configuration file."
					></PeersDefaultSettingsInput>
				</div>
			</div>
			<div class="card mb-4 shadow rounded-3">
				<p class="card-header">WireGuard Configurations Settings</p>
				<div class="card-body">
					<DashboardSettingsInputWireguardConfigurationPath
						targetData="wg_conf_path"
						title="Configurations Directory"
						:warning="true"
						warning-text="Remember to remove <code>/</code> at the end of your path. e.g <code>/etc/wireguard</code>"
					>
					</DashboardSettingsInputWireguardConfigurationPath>
				</div>
			</div>
			<div class="card mb-4 shadow rounded-3">
				<p class="card-header">Account Settings</p>
				<div class="card-body d-flex gap-4 flex-column">
					<AccountSettingsInputUsername targetData="username"
					                              title="Username"
					></AccountSettingsInputUsername>
					<hr class="m-0">
					<AccountSettingsInputPassword
						targetData="password">
					</AccountSettingsInputPassword>
					<hr class="m-0" v-if="!this.dashboardConfigurationStore.getActiveCrossServer()">
					<AccountSettingsMFA v-if="!this.dashboardConfigurationStore.getActiveCrossServer()"></AccountSettingsMFA>
				</div>
			</div>
			<DashboardAPIKeys></DashboardAPIKeys>
		</div>
	</div>
</template>

<style scoped>

</style>