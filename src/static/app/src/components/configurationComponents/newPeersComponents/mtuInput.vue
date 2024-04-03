<script>
export default {
	name: "mtuInput",
	props: {
		data: Object,
		saving: Boolean
	}
}
</script>

<template>
	<div>
		<label for="peer_mtu" class="form-label"><small class="text-muted">MTU</small></label>
		<input type="number" class="form-control form-control-sm rounded-3"
		       :disabled="this.saving"
		       v-model="this.data.mtu"
		       id="peer_mtu">
	</div>
</template>

<style scoped>

</style>