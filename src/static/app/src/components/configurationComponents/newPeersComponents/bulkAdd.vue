<script>
export default {
	name: "bulkAdd",
	props: {
		saving: Boolean,
		data: Object,
		availableIp: undefined
	}
}
</script>

<template>
	<div>
		<div class="form-check form-switch ">
			<input class="form-check-input"
			       type="checkbox" role="switch"
			       :disabled="!this.availableIp"
			       id="bulk_add" v-model="this.data.bulkAdd">
			<label class="form-check-label me-2" for="bulk_add">
				<small><strong>Bulk Add</strong></small>
			</label>
		</div>
		<p  :class="{'mb-0': !this.data.bulkAdd}"><small class="text-muted d-block">
			By adding peers by bulk, each peer's name will be auto generated, and Allowed IP will be assign to the next available IP.
		</small></p>

		<div class="form-group" v-if="this.data.bulkAdd">
			<input class="form-control form-control-sm rounded-3 mb-1" type="number" min="1"
			       :max="this.availableIp.length"
			       v-model="this.data.bulkAddAmount"
			       placeholder="How many peers you want to add?">
			<small class="text-muted">
				You can add up to <strong>{{this.availableIp.length}}</strong> peers
			</small>
		</div>
	</div>
</template>

<style scoped>

</style>