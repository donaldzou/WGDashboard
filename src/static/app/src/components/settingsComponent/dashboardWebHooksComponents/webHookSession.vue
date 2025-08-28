<script setup lang="ts">

import LocaleText from "@/components/text/localeText.vue";
import {computed} from "vue";
const props = defineProps(['session'])
const formattedBody = computed(() => {
	return JSON.stringify(props.session.Data, null, 4)
})
</script>

<template>
<div class="d-flex flex-column gap-3">
	<div>
		<small class="text-muted">
			<LocaleText t="Status"></LocaleText>
		</small>
		<h3 :class="{'text-success': session.Status === 0, 'text-danger': session.Status === 1}">
				<span v-if="session.Status === 0">
					<i class="bi bi-check-circle-fill me-2"></i><LocaleText t="Success"></LocaleText>
				</span>
			<span v-else-if="session.Status === 1">
					<i class="bi bi-x-circle-fill me-2"></i><LocaleText t="Failed"></LocaleText>
				</span>
			<span v-else-if="session.Status === -1">
					<i class="spinner-border me-2"></i><LocaleText t="Requesting..."></LocaleText>
				</span>
		</h3>
		<div class="d-flex gap-4 align-items-center">
			<div>
				<small class="text-muted">
					<LocaleText t="Started At"></LocaleText>
				</small>
				<h6>
					{{ session.StartDate }}
				</h6>
			</div>
			<div v-if="session.EndDate">
				<i class="bi bi-arrow-right"></i>
			</div>
			<div v-if="session.EndDate">
				<small class="text-muted">
					<LocaleText t="Ended At"></LocaleText>
				</small>
				<h6>
					{{ session.EndDate }}
				</h6>
			</div>
		</div>
	</div>

	<div>
		<h6>
			<LocaleText t="Logs"></LocaleText>
		</h6>
		<div class="table-responsive">
			<table class="table">
				<thead>
				<tr>
					<th scope="col">
						<LocaleText t="Datetime"></LocaleText>
					</th>
					<th scope="col">
						<LocaleText t="Status"></LocaleText>
					</th>
					<th scope="col">
						<LocaleText t="Message"></LocaleText>
					</th>
				</tr>
				</thead>
				<tbody>
				<tr v-for="log in [...session.Logs.Logs].reverse()">
					<td style="white-space: nowrap">
						{{ log.LogTime }}
					</td>
					<td style="white-space: nowrap" :class="{'text-success': log.Status === 0, 'text-danger': log.Status === 1}">
							<span v-if="log.Status === 0">
								<i class="bi bi-check-circle-fill me-2"></i>
							</span>
						<span v-else-if="log.Status === 1">
								<i class="bi bi-x-circle-fill me-2"></i>
							</span>
						<span v-else-if="log.Status === -1">
								<i class="bi bi-circle me-2"></i>
							</span>
					</td>
					<td  style="white-space: nowrap; overflow-x: scroll">
						{{ log.Message }}
					</td>
				</tr>
				</tbody>
			</table>
		</div>
	</div>

	<div>
		<h6>
			<LocaleText t="Data"></LocaleText>
		</h6>
		<div class="bg-body-tertiary p-3 rounded-3">
			<pre class="mb-0"><code>{{ formattedBody }}</code></pre>
		</div>
	</div>
</div>
</template>

<style scoped>

</style>