<script setup>
import {ref} from "vue";

const props = defineProps({
	mount: String,
	percentage: Number,
	align: Boolean
})

const show = ref(false)
</script>

<template>
	<div class="flex-grow-1 square rounded-3 border position-relative"
	     @mouseenter="show = true"
	     @mouseleave="show = false"
	     :style="{'background-color': `rgb(25 135 84 / ${percentage}%)`}">
		<Transition name="zoomReversed">
			<div
				v-if="show"
				style="white-space: nowrap;"
				class="floatingLabel z-3 border position-absolute d-block p-1 px-2 
				bg-body text-body rounded-3 border shadow d-flex"
				:class="[align ? 'end-0':'start-0']"
			>
				<small class="text-muted me-2">
					<samp>{{mount}}</samp>
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
}
</style>