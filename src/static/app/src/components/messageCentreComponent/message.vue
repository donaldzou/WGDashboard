<script>
export default {
	name: "message",
	props: {
		message: Object
	},
	mounted() {
		setTimeout(() => {
			this.message.show = false
		}, 5000)
	}
}
</script>

<template>
	<div class="card shadow rounded-3 position-relative mb-2" 
	     :class="{
			'text-bg-danger': this.message.type === 'danger', 
			'text-bg-success': this.message.type === 'success',
			'text-bg-warning': this.message.type === 'warning'}"
	     :id="this.message.id"
	     style="width: 400px">
		<div class="card-body">
			<small class="fw-bold d-block" style="text-transform: uppercase">FROM {{this.message.from}}</small>
			{{this.message.content}}
		</div>
	</div>
</template>

<style scoped>

</style>