<script setup>
import {reactive} from "vue";

const formData = reactive({
	username: "",
	email: "",
	password: ""
})
</script>

<template>
	<div class="d-flex vh-100 vw-100 p-4 overflow-y-scroll">
		<div class="m-auto" style="width: 600px">
			<h1 class="fw-bold display-4">Sign Up</h1>
		</div>
	</div>
</template>

<style scoped>

</style>