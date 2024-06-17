<script>


export default {
	name: "scheduleDropdown",
	props: {
		options: Array,
		data: String,
	},
	mounted() {
		console.log(this.options)
	},
	computed:{
		currentSelection(){
			return this.options.find(x => x.value === this.data)
		}
	}
}
</script>

<template>
	<div class="dropdown">
		<button class="btn btn-sm btn-outline-primary rounded-3" type="button" data-bs-toggle="dropdown" aria-expanded="false">
			<samp>{{this.currentSelection.display}}</samp>
		</button>
		<ul class="dropdown-menu rounded-3 shadow" style="font-size: 0.875rem; width: 200px">
			<li v-for="x in this.options">
				<a class="dropdown-item d-flex align-items-center" role="button" @click="$emit('update', x.value)">
					<samp>{{x.display}}</samp>
					<i class="bi bi-check ms-auto" v-if="x.value === this.currentSelection.value"></i>
				</a>
			</li>
		</ul>
	</div>
</template>

<style scoped>

</style>