<script setup lang="ts">
import {computed} from "vue";
import { fromString } from 'css-color-converter';

const props = defineProps(['group'])

const color = computed(() => {
	if (props.group.BackgroundColor){
		const cssColor = fromString(props.group.BackgroundColor)
		if (cssColor) {
			const rgb = cssColor.toRgbaArray()
			return +((rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 255000).toFixed(2) > 0.69 ? "#000":"#fff"
		}
	}
	return "#ffffff"
})
console.log(color)
</script>

<template>
<div :style="{'background-color': group.BackgroundColor }"
	 class="badge rounded-3 d-flex align-items-center overflow-scroll">
	<div
		aria-label="Pick icon button"
		style="height: 30px;"
		class="d-flex align-items-center border rounded-2 p-2 btn btn-sm">
		<i class="bi bi-pencil-fill"  :style="{color: color}"></i>
	</div>
	<div contenteditable="true" class="flex-grow-1 text-start d-flex align-items-center rounded-2"
		 :style="{color: color}"
		 style="height: 30px">
		Tag Name
	</div>
	<div style="height: 30px;"
		 aria-label="Pick color button"
		 class="d-flex align-items-center border-0 rounded-2 p-2 btn btn-sm">
		<i class="bi bi-palette-fill" :style="{color: color}"></i>
	</div>
	<div style="height: 30px;"
		 aria-label="Pick color button"
		 class="d-flex align-items-center border-0 rounded-2 p-2 btn btn-sm">
		<i class="bi bi-trash-fill" :style="{color: color}"></i>
	</div>
</div>
</template>

<style scoped>

</style>