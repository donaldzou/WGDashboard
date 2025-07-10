<script setup>
import {computed} from "vue";
import LocaleText from "@/components/text/localeText.vue";

const props = defineProps(['group', 'groupName', 'searchString', 'assignments'])
const emits = defineEmits(['count', 'assign'])

const filterGroup = computed(() => {
	let g = props.group.filter(x => 
		!props.assignments.map(a => a.Client.ClientID).includes(x.ClientID))
	
	if (props.searchString){
		let v = g.filter(
			x => (x.Name && x.Name.includes(props.searchString)) || (x.Email && x.Email.includes(props.searchString))
		)
		emits('count', v.length)
		return v
	}
	emits('count', g.length)
	return g
})
</script>

<template>
	<div class="d-flex flex-column gap-2">
		<h6 class="mb-0">
			<small>{{groupName}}</small>
		</h6>
		<div v-if="filterGroup.length > 0" class="d-flex flex-column gap-2">
			<div class="bg-body-secondary rounded-3 text-start p-2 d-flex p-1" role="button"
			     @click="emits('assign', client.ClientID)"
			     v-for="client in filterGroup">
				<small class="mb-0">
					{{ client.Email }}
				</small>
				<small class="text-muted ms-auto">{{ client.Name }}</small>
			</div>
		</div>
		<div v-else>
			<small class="text-muted">
				<LocaleText t="No result"></LocaleText>
			</small>
		</div>
	</div>
</template>

<style scoped>

</style>