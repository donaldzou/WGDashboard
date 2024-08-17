<script>
export default {
	name: "presharedKeyInput",
	props: {
		data: Object,
		saving: Boolean
	}
}
</script>

<template>
<div>
	<label for="peer_preshared_key_textbox" class="form-label">
		<small class="text-muted">Pre-Shared Key</small>
	</label>
	<input type="text" class="form-control form-control-sm rounded-3"
	       :disabled="this.saving"
	       v-model="this.data.preshared_key"
	       id="peer_preshared_key_textbox">
</div>
</template>

<style scoped>

</style>