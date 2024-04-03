<script>
export default {
	name: "nameInput",
	props: {
		bulk: Boolean,
		data: Object,
		saving: Boolean
	}
}
</script>

<template>
	<div :class="{inactiveField: this.bulk}">
		<label for="peer_name_textbox" class="form-label">
			<small class="text-muted">Name</small>
		</label>
		<input type="text" class="form-control form-control-sm rounded-3"
		       :disabled="this.saving || this.bulk"
		       v-model="this.data.name"
		       id="peer_name_textbox" placeholder="">
	</div>
</template>

<style scoped>

</style>