<script>
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
import LocaleText from "@/components/text/localeText.vue";
import DashboardLanguage from "@/components/settingsComponent/dashboardLanguage.vue";
import DashboardIPPortInput from "@/components/settingsComponent/dashboardIPPortInput.vue";
import DashboardSettingsWireguardConfigurationAutostart
	from "@/components/settingsComponent/dashboardSettingsWireguardConfigurationAutostart.vue";

export default {
	name: "settings",
	methods: {ipV46RegexCheck},
	components: {
		DashboardSettingsWireguardConfigurationAutostart,
		DashboardIPPortInput,
		DashboardLanguage,
		LocaleText,
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
}
</script>

<template>
	<div class="mt-md-5 mt-3 text-body mb-3">
		<div class="container-md d-flex flex-column gap-4">
			<div>
				<h2>
					<LocaleText t="WireGuard Configuration Settings"></LocaleText>
				</h2>
				<hr>
				<div class="card rounded-3 mb-3">
					<div class="card-body">
						<DashboardSettingsInputWireguardConfigurationPath
							targetData="wg_conf_path"
							title="Configurations Directory"
							:warning="true"
							warning-text="Remember to remove / at the end of your path. e.g /etc/wireguard"
						>
						</DashboardSettingsInputWireguardConfigurationPath>
					</div>
				</div>
				<div class="card rounded-3 mb-3">
					<div class="card-body">
						<DashboardSettingsWireguardConfigurationAutostart></DashboardSettingsWireguardConfigurationAutostart>
					</div>
				</div>
				<div class="card rounded-3 mb-3">
					<div class="card-body">
						<h5>
							<LocaleText t="Peer Default Settings"></LocaleText>
						</h5>
						<div>
							<PeersDefaultSettingsInput
								targetData="peer_global_dns" title="DNS"></PeersDefaultSettingsInput>
							<PeersDefaultSettingsInput
								targetData="peer_endpoint_allowed_ip" title="Endpoint Allowed IPs"></PeersDefaultSettingsInput>
							<PeersDefaultSettingsInput
								targetData="peer_mtu" title="MTU"></PeersDefaultSettingsInput>
							<PeersDefaultSettingsInput
								targetData="peer_keep_alive" title="Persistent Keepalive"></PeersDefaultSettingsInput>
							<PeersDefaultSettingsInput
								targetData="remote_endpoint" title="Peer Remote Endpoint"
								:warning="true" warningText="This will be changed globally, and will be apply to all peer's QR code and configuration file."
							></PeersDefaultSettingsInput>
						</div>
					</div>
				</div>
			</div>
			<div>
				<h2>
					<LocaleText t="WGDashboard Settings"></LocaleText>
				</h2>
				<hr>
				<div class="d-flex flex-column gap-3">
					<div class="card rounded-3">
						<div class="card-body">
							<div class="row g-2">
								<div class="col-sm">
									<DashboardTheme></DashboardTheme>
								</div>
								<div class="col-sm">
									<DashboardLanguage></DashboardLanguage>
								</div>
							</div>
						</div>
					</div>
					<div class="card">
						<div class="card-body">
							<DashboardIPPortInput></DashboardIPPortInput>
						</div>
					</div>
					<div class="card">
						<div class="card-body d-flex flex-column gap-3">
							<div>
								<h5>
									<LocaleText t="Account Settings"></LocaleText>
								</h5>
								<AccountSettingsInputUsername targetData="username"
								                              title="Username"
								></AccountSettingsInputUsername>
							</div>
							<div>
								<h6>
									<LocaleText t="Update Password"></LocaleText>
								</h6>
								<AccountSettingsInputPassword
									targetData="password">
								</AccountSettingsInputPassword>
							</div>

							<AccountSettingsMFA v-if="!this.dashboardConfigurationStore.getActiveCrossServer()"></AccountSettingsMFA>
						</div>
					</div>
					<DashboardAPIKeys></DashboardAPIKeys>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>