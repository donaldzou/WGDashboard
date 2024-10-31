<script setup>
import LocaleText from "@/components/text/localeText.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {computed, reactive, ref, watch} from "vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import {fetchPost} from "@/utilities/fetch.js";
const store = DashboardConfigurationStore()
const wireguardConfigurationStore = WireguardConfigurationsStore()
const data = ref(store.Configuration.WireGuardConfiguration.autostart)

const configurations = computed(() => {
	return wireguardConfigurationStore.Configurations.map(x => x.Name)
})

const updateAutostart = async () => {
	console.log(data.value)
	await fetchPost("/api/updateDashboardConfigurationItem", {
		section: "WireGuardConfiguration",
		key: "autostart",
		value: data.value
	}, async (res) => {
		console.log(res);
	})
}

const toggle = (c) => {
	if (data.value.includes(c)){
		data.value = data.value.filter(x => x !== c)
	}else{
		data.value.push(c)
	}
}

watch(data.value, () => {
	updateAutostart()
})

</script>

<template>
<div class="card rounded-3">
	<div class="card-header">
		<h6 class="my-2">
			<LocaleText t="Toggle When Start Up"></LocaleText>
		</h6>
	</div>
	<div class="card-body d-flex gap-2">
		<div class="list-group w-100">
			<button type="button" 
			        :key="c"
			        @click="toggle(c)"
			        class="list-group-item list-group-item-action py-2 w-100 d-flex align-items-center"
			        v-for="c in configurations">
				<samp>{{c}}</samp>
				<i class="ms-auto" :class="[data.includes(c) ? 'bi-check-circle-fill':'bi-circle']"></i>
			</button>
		</div>
	</div>
</div>
</template>

<style scoped>
.list-group{
	
	&:first-child{
		border-top-left-radius: var(--bs-border-radius-lg);
		border-top-right-radius: var(--bs-border-radius-lg)
	}
	&:last-child{
		border-bottom-left-radius: var(--bs-border-radius-lg);
		border-bottom-right-radius: var(--bs-border-radius-lg)
	}
	
}
</style>