<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import {computed, ref} from "vue";
import {fetchGet} from "@/utilities/fetch.js"
import NewConfigurationTemplate from "@/components/newConfigurationComponents/newConfigurationTemplate.vue";
const emits = defineEmits(['subnet', 'port'])
const templates = ref([])

const getTemplates = async () => {
	await fetchGet('/api/newConfigurationTemplates', {}, (res) => {
		templates.value = res.data
	})
}

await getTemplates()

const newTemplates = ref([])
const newTemplate = async () => {
	await fetchGet('/api/newConfigurationTemplates/createTemplate', {}, (res) => {
		newTemplates.value.push(res.data)
	})
}

const numberOfIP = ref(256)
const calculateIP = ref(256)

</script>

<template>
<div class="card">
	<div class="card-header">
		<div class="d-flex align-items-center">
			<LocaleText t="Templates"></LocaleText>
			<button
				type="button"
				@click="newTemplate()"
				class="btn btn-sm bg-success-subtle text-success-emphasis border-success-subtle rounded-3 ms-auto">
				<i class="bi bi-plus-circle me-2"></i><LocaleText t="Add Template"></LocaleText>
			</button>
		</div>
		<small class="text-muted">
			<LocaleText t="Create templates to keep track a list of available Subnets & Listen Ports"></LocaleText>
		</small>
	</div>
	<div class="card-body">
		<div class="d-flex gap-2 align-items-center mb-2" v-if="templates.length > 0">
			<label class="text-muted"  style="white-space: nowrap">
				<small><LocaleText t="No. of IP Address / Subnet"></LocaleText></small>
			</label>
			<input type="number"
				   v-model="numberOfIP"
				   @change="calculateIP = numberOfIP"
				   class="form-control form-control-sm rounded-3 w-100 ms-auto">
		</div>
		<div class="row g-2">
			<div class="col-12" v-if="newTemplates.length === 0 && templates.length === 0">
				<p class="text-center text-muted m-0">
					<LocaleText t="No Templates"></LocaleText>
				</p>
			</div>
			<div class="col-12" v-for="template in newTemplates">
				<NewConfigurationTemplate
					:edit="true"
					:isNew="true"
					@remove="newTemplates = newTemplates.filter(x => x.TemplateID !== template.TemplateID)"
					@update="newTemplates = newTemplates.filter(x => x.TemplateID !== template.TemplateID); getTemplates()"
					@subnet="args => emits('subnet', args)"
					@port="args => emits('port', args)"
					:template="template"></NewConfigurationTemplate>
			</div>
			<div class="col-12" v-for="(template, index) in templates">
				<NewConfigurationTemplate
					:key="template.TemplateID"
					:peersCount="calculateIP"
					@remove="getTemplates()"
					@update="getTemplates()"
					@subnet="args => emits('subnet', args)"
					@port="args => emits('port', args)"
					:template="template"></NewConfigurationTemplate>
			</div>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>