<script>
import ScheduleDropdown from "@/components/configurationComponents/peerScheduleJobsComponents/scheduleDropdown.vue";

export default {
	name: "schedulePeerJob",
	components: {ScheduleDropdown},
	props: {
		dropdowns: Array[Object],
		job: Object
	}
}
</script>

<template>
	<div class="card shadow-sm rounded-3">
		<div class="card-header bg-transparent text-muted border-0">
			<small class="d-flex">
				<strong class="me-auto">Job ID</strong>
				{{this.job.JobID}}
			</small>
		</div>
		<div class="card-body pt-1">
			<div class="d-flex gap-3 align-items-center mb-2">
				<samp>
					if
				</samp>
				<ScheduleDropdown
					:options="this.dropdowns.Field"
					:data="this.job.Field"
					@update="(value) => this.job.Field = value"
				></ScheduleDropdown>
				<samp>
					is
				</samp>
				<ScheduleDropdown
					:options="this.dropdowns.Operator"
					:data="this.job.Operator"
					@update="(value) => this.job.Operator = value"
				></ScheduleDropdown>
				<input class="form-control form-control-sm form-control-dark rounded-3 flex-grow-1" style="width: auto">
				<samp>
					{
				</samp>
			</div>
			<div class="px-5 d-flex gap-3 align-items-center">
				<samp>
					execute
				</samp>
				<ScheduleDropdown
					:options="this.dropdowns.Action"
					:data="this.job.Action"
					@update="(value) => this.job.Action = value"
				></ScheduleDropdown>
				<samp>
					;
				</samp>
			</div>
			<div>
				<samp>}</samp>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>