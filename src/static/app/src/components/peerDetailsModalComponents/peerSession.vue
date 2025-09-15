<script setup lang="ts">
import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";

dayjs.extend(customParseFormat);
const props = defineProps(['session'])

const heightPerSecond = 1224 / 24 / 60 / 60;
const start = dayjs(props.session.timestamps[0])
const offsetTop = (start.hour() * 60 * 60 + start.minute() * 60 + start.second()) * heightPerSecond

const duration = dayjs(props.session.duration, "HH:mm:ss")
const height = (duration.hour() * 60 * 60 + duration.minute() * 60 + duration.second()) * heightPerSecond

console.log()
</script>

<template>
	<div class="position-absolute"
		 :style="{top: offsetTop + 'px'}"
		 style="width: 100%; padding-left: calc(18px + 2.5rem)">
		<div class="rounded-3"
			 style="background: rgba(25,135,84,0.7); min-height: 5px !important;"
			 :style="{height: height + 'px'}">

		</div>
	</div>
</template>

<style scoped>

</style>