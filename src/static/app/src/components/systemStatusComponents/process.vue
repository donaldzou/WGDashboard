<script setup>
const props = defineProps(["process", "cpu"])

</script>

<template>
	<div class="mb-1 d-flex gap-5">
		<small class="title">
			<i class="bi bi-code-square me-2"></i>
			<samp>{{process.command ? process.command : process.name}}</samp>
		</small>
		<small class="ms-auto">
			{{(Math.round((process.percent + Number.EPSILON) * 10) / 10)}}%
		</small>
	</div>
</template>

<style scoped>
.title{
	height: 18px;
	text-overflow: ellipsis;
	overflow: hidden;
	white-space: nowrap;
}
</style>