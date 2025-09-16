<script setup lang="ts">
import dayjs from "dayjs";
import {computed, ref} from "vue";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore"
dayjs.extend(isSameOrBefore)
const props = defineProps(['sessions'])
const offsetMonth = ref(0)
const today = ref(dayjs().subtract(offsetMonth.value, 'month'))
const firstDay = ref(today.value.startOf('month'))
const lastDay = ref(today.value.endOf('month'))

const startOfWeek = ref(firstDay.value.startOf('week'))
const endOfWeek = ref(lastDay.value.endOf('week'))

const calendarDays = computed(() => {
	let dates = []
	let cur = startOfWeek.value;
	while (cur.isSameOrBefore(endOfWeek.value, 'day')){
		dates.push(cur)
		cur = cur.add(1, 'day')
	}
	return dates
})
</script>

<template>
<div class="calendar-grid">
	<div class="calendar-day p-2"
		 :class="{
			'bg-body-secondary': day.isSame(today, 'D'),
			'border-end': day.day() < 6,
			'border-bottom': index < 28}"
		 v-for="(day, index) in calendarDays">
		<h5>
			{{ day.isSame(day.startOf('month')) ? day.format("MMM") : '' }} {{ day.format('D')}}
		</h5>
	</div>
</div>
</template>

<style scoped>
.calendar-grid{
	display: grid;
	grid-template-areas: "sun mon tue wed thu fri sat";
	grid-template-columns: repeat(7, 1fr);
}

.calendar-day.day-6{
	border-right: none !important;
}



.calendar-day{
	min-height: 150px;
}



.calendar-day.active{

}
</style>