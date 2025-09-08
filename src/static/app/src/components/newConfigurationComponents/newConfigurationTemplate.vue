<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import {computed, onMounted, reactive, ref, watch} from "vue";
import {containsCidr, expandCidr, mergeCidr, parseCidr} from "cidr-tools";
import {fetchPost} from "@/utilities/fetch.js"
const props = defineProps(['template', 'edit', 'isNew', 'peersCount'])
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore";
const store = WireguardConfigurationsStore()
const edit = ref(false)
if (props.edit){
	edit.value = true
}
const data = ref({...props.template})


const peersCount = ref(256)
const groups = ref([])
const show = ref(20)
const emits = defineEmits(['subnet', 'port', 'update', 'remove'])
const selectedSubnet = ref(undefined)
const selectedPort = ref(undefined)
const ports = ref([])
const availableSubnets = () => {
	groups.value = []
	if (props.template.Subnet){
		let templateExpand = new Set([...expandCidr(props.template.Subnet)])
		if (props.peersCount && props.peersCount > 0){
			for (let c of store.Configurations){
				let address = c.Address.replace(" ", "").split(",")
				for (let a of address){
					if (containsCidr(props.template.Subnet, a)){
						templateExpand = templateExpand.difference(
							new Set([...expandCidr(a)])
						)
					}
				}
			}
			let groupsCount = Math.floor(templateExpand.size / props.peersCount)
			let sliced = 0
			templateExpand = Array.from(templateExpand)
			for (let g = 0; g < (groupsCount > 10 ? 10 : groupsCount); g++){
				groups.value.push(mergeCidr(templateExpand.slice(sliced, sliced + props.peersCount)))
				sliced += props.peersCount
			}

		}
	}
}
const availablePorts = () => {
	if (props.template.ListenPortStart && props.template.ListenPortEnd){
		let start = props.template.ListenPortStart
		let end = props.template.ListenPortEnd
		if (start > end){
			start = props.template.ListenPortEnd
			end = props.template.ListenPortStart
		}
		let p = new Set(Array.from(
			{
				length: end - start + 1
			}, (val, index) => start + index
		))
		ports.value = [...p.difference(new Set(store.Configurations.map(
			c => Number(c.ListenPort)
		)))]
	}
}

onMounted(() => {
	if (!props.isNew){
		availableSubnets()
		availablePorts()
	}
})

watch(() => props.peersCount, () => {
	availableSubnets()
})

watch(selectedSubnet, () => {
	emits("subnet", selectedSubnet.value)
})

watch(selectedPort, () => {
	emits("port", selectedPort.value)
})

watch(() => props.template, () => {
	availableSubnets()
	availablePorts()
}, {
	deep: true
})

const readyToSave = computed(() => {
	try{
		const {start, end} = parseCidr(data.value.Subnet)
		if (end - start >= 1000000n) {
			throw new Error("Too many IPs");
		}
		return data.value.Subnet && data.value.ListenPortStart && data.value.ListenPortEnd && (data.value.ListenPortEnd >= data.value.ListenPortStart)
	}catch (e){
		return false
	}
})

const saveTemplate = async () => {
	await fetchPost("/api/newConfigurationTemplates/updateTemplate", {
		Template: data.value
	}, (res) => {
		if (res.status){
			emits('update', data.value)
			edit.value = false

		}
	})
}

const deleteTemplate = async () => {
	await fetchPost("/api/newConfigurationTemplates/deleteTemplate", {
		Template: data.value
	}, (res) => {
		if (res.status){
			emits('remove', data)
		}
	})
}

</script>

<template>
<div class="card rounded-3">
	<div class="card-body ">
		<div class="row">
			<div class="col-sm">
				<div class="d-flex flex-column gap-2">
					<div class="d-flex align-items-center">
						<label class="text-muted">
							<small><LocaleText t="Subnet"></LocaleText></small>
						</label>
						<p class="mb-0 ms-auto" v-if="!edit"><small>{{ template.Subnet }}</small></p>
						<input class="form-control-sm form-control rounded-3 w-auto ms-auto" v-model="data.Subnet" v-else>
					</div>

					<div class="d-flex gap-2 flex-column" v-if="!edit">
						<label class="text-muted d-flex align-items-center gap-1" style="white-space: nowrap">
							<small><LocaleText t="Available Subnets"></LocaleText></small>
							<span class="badge rounded-pill text-bg-success ms-auto">
						{{ groups.length }}
					</span>
						</label>
						<select
							v-model="selectedSubnet"
							class="form-select form-select-sm rounded-3 w-100 ms-auto">
							<option :value="undefined" disabled>
								<LocaleText t="Select..."></LocaleText>
							</option>
							<option v-for="s in groups" :value='s.join(", ")'>
								{{ s.join(", ") }}
							</option>
						</select>
					</div>
				</div>
			</div>
			<div class="col-sm">
				<div class="d-flex flex-column gap-2 h-100">
					<div class="d-flex align-items-center">
						<label class="text-muted">
							<small><LocaleText t="Listen Port Range"></LocaleText></small>
						</label>
						<p class="mb-0 ms-auto" v-if="!edit">
							<small>
								{{ template.ListenPortStart }}<i class="bi bi-arrow-right mx-2"></i>
								{{ template.ListenPortEnd }}
							</small>
						</p>
						<div v-else class="d-flex ms-auto align-items-center">
							<input class="form-control-sm form-control rounded-3  ms-auto"
								   style="width: 80px"
								   v-model="data.ListenPortStart"
								   type="number"
							>
							<i class="bi bi-arrow-right mx-2"></i>
							<input class="form-control-sm form-control rounded-3  ms-auto"
								   style="width: 80px"
								   v-model="data.ListenPortEnd"
								   type="number"
							>
						</div>
					</div>
					<div class="d-flex gap-2 flex-column mt-auto" v-if="!edit">
						<label class="text-muted d-flex align-items-center gap-1" style="white-space: nowrap">
							<small><LocaleText t="Available Ports"></LocaleText></small>
							<span class="badge rounded-pill text-bg-success ms-auto">
								{{ ports.length }}
							</span>
						</label>
						<select
							v-model="selectedPort"

							class="form-select form-select-sm rounded-3 w-100 ms-auto">
							<option :value="undefined" disabled>
								<LocaleText t="Select..."></LocaleText>
							</option>
							<option v-for="p in [...ports]" :value='p'>
								{{ p }}
							</option>

						</select>
					</div>
				</div>
			</div>
		</div>
		<hr>
		<div class="d-flex gap-2" v-if="!edit">
			<button
				type="button"
				@click="edit = true; data = {...props.template}"
				class="ms-auto btn btn-sm border-primary-subtle bg-primary-subtle text-primary-emphasis rounded-3">
				<LocaleText t="Edit"></LocaleText>
			</button>
			<button
				type="button"
				@click="deleteTemplate()"
				class="btn btn-sm border-danger-subtle bg-danger-subtle text-danger-emphasis rounded-3">
				<LocaleText t="Delete"></LocaleText>
			</button>
		</div>
		<div class="d-flex gap-2" v-else>
			<button
				type="button"
				@click="isNew ? emits('remove') : edit = false"
				class="ms-auto btn btn-sm border-secondary-subtle bg-secondary-subtle text-secondary-emphasis rounded-3">
				<LocaleText t="Cancel"></LocaleText>
			</button>
			<button
				type="button"
				@click="saveTemplate()"
				:class="{disabled: !readyToSave}"
				class="btn btn-sm border-primary-subtle bg-primary-subtle text-primary-emphasis rounded-3">
				<LocaleText t="Save"></LocaleText>
			</button>
		</div>

	</div>
</div>
</template>

<style scoped>

</style>