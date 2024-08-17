<script>
export default {
	name: "persistentKeepAliveInput",
	props: {
		data: Object,
		saving: Boolean
	}
}
</script>

<template>
<div>
	<label for="peer_keep_alive" class="form-label">
		<small class="text-muted">Persistent Keepalive</small>
	</label>
	<input type="number" class="form-control form-control-sm rounded-3"
	       :disabled="this.saving"
	       v-model="this.data.keepalive"
	       id="peer_keep_alive">
</div>
</template>

<style scoped>

</style>