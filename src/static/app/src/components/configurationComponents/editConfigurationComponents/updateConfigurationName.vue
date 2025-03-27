<script setup>
import {onMounted, reactive, ref, watch} from "vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import LocaleText from "@/components/text/localeText.vue";
import {fetchPost} from "@/utilities/fetch.js";
import {useRouter} from "vue-router";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
const props = defineProps({
	configurationName: String
})
const emit = defineEmits(['close'])
const newConfigurationName = reactive({
	data: "",
	valid: false
});
const store = WireguardConfigurationsStore()

onMounted(() => {
	watch(() => newConfigurationName.data, (newVal) => {
		newConfigurationName.valid = /^[a-zA-Z0-9_=+.-]{1,15}$/.test(newVal) && newVal.length > 0 && !store.Configurations.find(x => x.Name === newVal);
	})
})
const dashboardConfigurationStore = DashboardConfigurationStore()
const loading = ref(false)
const router = useRouter()
const rename = async () => {
	if (newConfigurationName.data){
		loading.value = true
		clearInterval(dashboardConfigurationStore.Peers.RefreshInterval)
		await fetchPost("/api/renameWireguardConfiguration", {
			ConfigurationName: props.configurationName,
			NewConfigurationName: newConfigurationName.data
		}, async (res) => {
			if (res.status){
				await store.getConfigurations()
				dashboardConfigurationStore.newMessage("Server", "Configuration renamed", "success")
				router.push(`/configuration/${newConfigurationName.data}/peers`)
			}else{
				dashboardConfigurationStore.newMessage("Server", res.message, "danger")
				loading.value = false
			}
			
		})
	}
}
</script>

<template>
<div class="card rounded-3 flex-grow-1 bg-danger-subtle border-danger-subtle border shadow">
	<div class="card-body">
		<p>
			<LocaleText t="To update this configuration's name, WGDashboard will execute the following operations:"></LocaleText>
		</p>
		<ol>
			<li>
				<LocaleText t="Duplicate current configuration's database table and .conf file with the new name"></LocaleText>
			</li>
			<li>
				<LocaleText t="Delete current configuration's database table and .conf file"></LocaleText>
			</li>
		</ol>
		<div class="d-flex align-items-center gap-3 inputGroup">
			<input class="form-control form-control-sm rounded-3" :value="configurationName" disabled>
			<h3 class="mb-0">
				<i class="bi bi-arrow-right"></i>
			</h3>
			<input class="form-control form-control-sm rounded-3"
			       id="newConfigurationName"
			       :class="[newConfigurationName.data ? (newConfigurationName.valid ? 'is-valid' : 'is-invalid') : '']"
			       v-model="newConfigurationName.data">
		</div>
		<div class="invalid-feedback" :class="{'d-block': !newConfigurationName.valid && newConfigurationName.data}">
			<LocaleText t="Configuration name is invalid. Possible reasons:"></LocaleText>
			<ul class="mb-0">
				<li>
					<LocaleText t="Configuration name already exist."></LocaleText>
				</li>
				<li>
					<LocaleText t="Configuration name can only contain 15 lower/uppercase alphabet, numbers, underscore, equal sign, plus sign, period and hyphen."></LocaleText>
				</li>
			</ul>
		</div>
		<div class="d-flex mt-3">
			<button
				@click="emit('close')"
				class="btn btn-sm bg-secondary-subtle border-secondary-subtle text-secondary-emphasis rounded-3">
				<LocaleText t="Cancel"></LocaleText>
			</button>
			<button
				@click="rename()"
				:disabled="!newConfigurationName.data || loading"
				class="btn btn-sm btn-danger rounded-3 ms-auto">
				<LocaleText t="Save"></LocaleText>
			</button>
		</div>
	</div>
</div>
</template>

<style scoped>
@media screen and (max-width: 567px) {
	.inputGroup{
		flex-direction: column;
		
		h3{
			transform: rotate(90deg);
		}
	}
}
</style>