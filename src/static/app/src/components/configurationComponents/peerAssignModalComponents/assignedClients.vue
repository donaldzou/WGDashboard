<script setup>
import LocaleText from "@/components/text/localeText.vue";
const props = defineProps(['assignments'])
const emits = defineEmits(['unassign'])
</script>

<template>
	<div class="p-3 bg-body-tertiary rounded-3 d-flex flex-column gap-2">
		<h6 class="mb-0">
			<LocaleText t="Assigned Clients"></LocaleText>
		</h6>
		<TransitionGroup name="list" tag="div" class="position-relative">
			<div class="bg-body-secondary rounded-3 text-start p-2 d-flex mb-2 assignment"
			     :key="a.AssignmentID"
			     v-for="a in assignments">
				<div class="d-flex flex-column">
					<small>
						{{ a.Client.Email }}
					</small>
					<small class="text-muted">
						{{ a.Client.Name ? a.Client.Name + ' | ' : '' }}{{ a.Client.ClientGroup ? a.Client.ClientGroup : 'Local' }}
					</small>
				</div>
				<button
					@click="emits('unassign', a.AssignmentID)"
					aria-label="Delete Assignment"
					class="btn bg-danger-subtle text-danger-emphasis ms-auto">
					<i class="bi bi-trash-fill"></i>
				</button>
			</div>
		</TransitionGroup>
		<div class="text-center" v-if="assignments.length === 0">
			<small class="text-muted">
				<LocaleText t="No client assigned to this peer yet"></LocaleText>
			</small>
		</div>
	</div>
</template>

<style scoped>
.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
	transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
	opacity: 0;
	transform: scale(0.9);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
	position: absolute;
	width: 100%;
}

.assignment:last-child{
	margin-bottom: 0 !important;
}
</style>