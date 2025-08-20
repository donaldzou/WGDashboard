<script setup lang="ts">
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

import LocaleText from "@/components/text/localeText.vue";
import DashboardLanguage from "@/components/settingsComponent/dashboardLanguage.vue";
import AccountSettingsInputPassword from "@/components/settingsComponent/accountSettingsInputPassword.vue";
import DashboardTheme from "@/components/settingsComponent/dashboardTheme.vue";
import DashboardAPIKeys from "@/components/settingsComponent/dashboardAPIKeys.vue";
import DashboardIPPortInput from "@/components/settingsComponent/dashboardIPPortInput.vue";
import AccountSettingsMFA from "@/components/settingsComponent/accountSettingsMFA.vue";
import AccountSettingsInputUsername from "@/components/settingsComponent/accountSettingsInputUsername.vue";
import DashboardEmailSettings from "@/components/settingsComponent/dashboardEmailSettings.vue";
import DashboardWebHooks from "@/components/settingsComponent/dashboardWebHooks.vue";

const dashboardConfigurationStore = DashboardConfigurationStore()

</script>

<template>
	<div class="d-flex gap-3 flex-column">
		<div class="card rounded-3">
			<div class="card-header">
				<h6 class="my-2">
					<LocaleText t="Appearance"></LocaleText>
				</h6>
			</div>
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
			<div class="card-header">
				<h6 class="my-2">
					<LocaleText t="Dashboard IP Address & Listen Port"></LocaleText>
				</h6>
			</div>
			<div class="card-body">
				<DashboardIPPortInput></DashboardIPPortInput>
			</div>
		</div>
		<div class="card">
			<div class="card-header">
				<h6 class="my-2">
					<LocaleText t="Account Settings"></LocaleText>
				</h6>
			</div>
			<div class="card-body d-flex flex-column gap-3">
				<div>
					<AccountSettingsInputUsername targetData="username"
												  title="Username"
					></AccountSettingsInputUsername>
				</div>
				<hr>
				<div>
					<AccountSettingsInputPassword
						targetData="password">
					</AccountSettingsInputPassword>
				</div>
			</div>
		</div>
		<div class="card">
			<div class="card-header">
				<h6 class="my-2">
					<LocaleText t="Multi-Factor Authentication (MFA)"></LocaleText>
				</h6>
			</div>
			<div class="card-body">
				<AccountSettingsMFA v-if="!dashboardConfigurationStore.getActiveCrossServer()"></AccountSettingsMFA>
			</div>
		</div>
		<DashboardAPIKeys></DashboardAPIKeys>
		<DashboardEmailSettings></DashboardEmailSettings>
		<DashboardWebHooks></DashboardWebHooks>
	</div>
</template>

<style scoped>

</style>