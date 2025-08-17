<script setup lang="ts">
import { fromString } from 'css-color-converter';
import {computed} from "vue";

const props = defineProps(["BackgroundColor", "GroupName", "Icon"])

const color = computed(() => {
	if (props.BackgroundColor){
		const cssColor = fromString(props.BackgroundColor)
		if (cssColor) {
			const rgb = cssColor.toRgbaArray()
			return +((rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 255000).toFixed(2)
		}
	}
	return 0
})
</script>

<template>
<span
	class="badge rounded-3 shadow"
	:style="{'background-color': BackgroundColor, 'color': color > 0.69 ? '#000':'#fff' }"
>
	<i class="bi me-1" :class="Icon" v-if="Icon"></i>#{{ GroupName }}
</span>
</template>

<style scoped>

</style>