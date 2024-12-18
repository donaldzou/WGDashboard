<script setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
const observer = ref(undefined);
const emits = defineEmits(['loadMore'])
const props = defineProps(['peerListLength', 'showPeersCount'])

onMounted(() => {
	observer.value = new IntersectionObserver((entries) => {
		entries.forEach(e => {
			if (e.isIntersecting){
				emits('loadMore');
			}
		})}, {
		rootMargin: "20px",
		threshold: 1.0,
	})
	observer.value.observe(document.querySelector("#loadMore"))
})

onBeforeUnmount(() =>{
	observer.value.disconnect();
})

</script>

<template>
	<div class="text-center">
		<small v-if="peerListLength < showPeersCount" class="text-muted">
			That's it, no more peers
		</small>
		<div style="margin-bottom: 20px; height: 1px" id="loadMore"></div>
	</div>
</template>

<style scoped>

</style>