<script setup lang="ts">
import {computed} from "vue";
import LocaleText from "@/components/text/localeText.vue";

const props = defineProps(['groupName', 'clients', 'searchString'])

const getClients = computed(() => {
	const s = props.searchString.toLowerCase()
	if (!props.searchString){
		return props.clients
	}
	return props.clients.filter(
		x =>
			(x.ClientID && x.ClientID.toLowerCase().includes(s)) || 
			(x.Email && x.Email.toLowerCase().includes(s) || 
				(x.Name && x.Name.toLowerCase().includes(s)))
	)
})
</script>

<template>
	<div class="card rounded-3">
		<div class="card-header d-flex align-items-center">
			{{ groupName }}
			<span class="badge text-bg-primary ms-auto">
				<LocaleText :t="getClients.length + ' Clients'"></LocaleText>
			</span>
		</div>
		<div class="card-body">
			<small class="text-muted" v-if="getClients.length === 0">
				<LocaleText :t="'No clients contains ' + searchString"></LocaleText>
			</small>
			<div class="row g-2" v-else>
				<div class="col-sm-4" v-for="clients in getClients">
					<div class="p-3 bg-body-tertiary border rounded-3 shadow" role="button">
						<div>
							<small class="text-muted">
								<LocaleText t="Client ID"></LocaleText>
							</small>
							<p class="mb-0">
								<samp style="font-size: 0.875rem">{{ clients.ClientID }}</samp>
							</p>
						</div>
						<div>
							<small class="text-muted">
								<LocaleText t="Email"></LocaleText>
							</small>
							<p class="mb-0">
								{{ clients.Email }}
							</p>
						</div>
						<div>
							<small class="text-muted">
								<LocaleText t="Name"></LocaleText>
							</small>
							<p class="mb-0" :class="{'text-muted': !clients.Name}">
								{{ clients.Name ? clients.Name : 'N/A' }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>