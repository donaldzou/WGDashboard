<script setup>
import {computed, ref} from "vue";

const props = defineProps({
	mount: Object,
	align: Boolean,
	square: Boolean
})

const show = ref(false)

const squareHeight = computed(() => {
	return props.square ? "40px": "25px"
})
</script>

<template>
	<div class="flex-grow-1 square rounded-3 border position-relative"
	     @mouseenter="show = true"
	     @mouseleave="show = false"
	     :style="{'background-color': `rgb(25 135 84 / ${mount.percent}%)`}">
		<Transition name="zoomReversed">
			<div
				v-if="show"
				style="white-space: nowrap;"
				:style="{'top': squareHeight}"
				class="floatingLabel z-3 border position-absolute d-block p-1 px-2 
				bg-body text-body rounded-3 border shadow d-flex"
				:class="[align ? 'end-0':'start-0']"
			>
				<small class="text-muted me-2">
					<samp>{{mount.mountPoint}}</samp>
				</small>
				<small class="fw-bold">
					{{mount.percent}}%
				</small>
			</div>
		</Transition>
	</div>
</template>

<style scoped>
.square{
	height: v-bind(squareHeight);
	transition: background-color 0.5s cubic-bezier(0.42, 0, 0.22, 1.0);
}
</style>