<script setup>
import {ref} from "vue";

const props = defineProps({
	core_number: Number,
	percentage: Number
})

const show = ref(false)
</script>

<template>
	<div class="flex-grow-1 square rounded-3 border position-relative"
	     @mouseenter="show = true"
	     @mouseleave="show = false"
	     :style="{'background-color': `rgb(13 110 253 / ${percentage*10}%)`}">
		<Transition name="zoomReversed">
			<div
				v-if="show"
				style="white-space: nowrap;"
				class="floatingLabel z-3 border position-absolute d-block p-1 px-2 
				bg-body text-body rounded-3 border shadow d-flex">
				<small class="text-muted me-2">
					Core #{{core_number + 1}}
				</small>
				<small class="fw-bold">
					{{percentage}}%
				</small>
			</div>
		</Transition>
	</div>
</template>

<style scoped>
.square{
	height: 25px;
	transition: background-color 0.5s cubic-bezier(0.42, 0, 0.22, 1.0);
}

.floatingLabel{
	top: 25px;
	left: 0;
	
}
</style>