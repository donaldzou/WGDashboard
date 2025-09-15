<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import { fetchGet } from "@/utilities/fetch.js"
import {computed, onBeforeUnmount, ref, watch} from "vue";

const props = defineProps(['selectedPeer', 'selectedDate'])

import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js"
const store = DashboardConfigurationStore()
const sessions = ref([])
import dayjs from "dayjs";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore"
import PeerSessionCalendarDay from "@/components/peerDetailsModalComponents/peerSessionCalendarDay.vue";
dayjs.extend(isSameOrBefore)
const interval = ref(undefined)
const offsetMonth = ref(0)
const todayNoOffset = ref(dayjs())
const today = computed(() => dayjs().add(offsetMonth.value, 'month'))
const firstDay = computed(() => today.value.startOf('month'))
const lastDay = computed(() => today.value.endOf('month'))

const startOfWeek = computed(() => firstDay.value.startOf('week'))
const endOfWeek = computed(() => lastDay.value.endOf('week'))

const calendarDays = computed(() => {
	let dates = []
	let cur = startOfWeek.value;
	while (cur.isSameOrBefore(endOfWeek.value, 'day')){
		dates.push(cur)
		cur = cur.add(1, 'day')
	}
	if (dates.length < 42){
		let q = 42 - dates.length
		for (let i = 0; i < q; i++){
			console.log('push')
			dates.push(cur)
			cur = cur.add(1, 'day')
		}
	}
	return dates
})

const getSessions = async () => {
	await fetchGet("/api/getPeerSessions", {
		configurationName: props.selectedPeer.configuration.Name,
		id: props.selectedPeer.id,
		startDate: startOfWeek.value.format("YYYY-MM-DD"),
		endDate: endOfWeek.value.format("YYYY-MM-DD")
	}, (res) => {
		sessions.value = res.data.reverse()
	})
}

getSessions()
interval.value = setInterval(async () => {
	await getSessions()
}, 60000)

onBeforeUnmount(() => {
	clearInterval(interval.value)
})

watch(() => today.value, () => getSessions())

const dayDetails = ref(false)
const dayDetailsData = ref(undefined)
const emits = defineEmits(['selectDate'])
</script>

<template>
	<div>

		<div class="card rounded-3 bg-transparent">
			<div class="card-header d-flex align-items-center">
				<button class="btn btn-sm rounded-3" @click="offsetMonth -= 1">
					<i class="bi bi-chevron-left"></i>
				</button>
				<button class="btn btn-sm rounded-3" v-if="offsetMonth !== 0" @click="offsetMonth = 0; $emit('selectDate', day)">
					<LocaleText t="Today"></LocaleText>
				</button>
				<h5 class="mx-auto mb-0 text-center">
					<small class="text-muted" style="font-size: 0.9rem">
						<LocaleText t="Peer Historical Sessions"></LocaleText>
					</small><br>
					{{ today.format('YYYY / MM')}}
				</h5>
				<button class="btn btn-sm rounded-3" v-if="offsetMonth !== 0" @click="offsetMonth = 0; $emit('selectDate', day)">
					<LocaleText t="Today"></LocaleText>
				</button>
				<button class="btn btn-sm rounded-3" @click="offsetMonth += 1">
					<i class="bi bi-chevron-right"></i>
				</button>
			</div>
			<div class="card-body p-0 position-relative">
				<div class="calendar-grid">
					<div class="calendar-day p-2 d-flex flex-column"
						 :key="day"
						 @click="$emit('selectDate', day)"
						 style="cursor: pointer"
						 :class="{
						'bg-body-secondary': day.isSame(todayNoOffset, 'D'),
						'border-end': day.day() < 6,
						'border-bottom': index < calendarDays.length - 7,
						'extra-day': !day.isSame(today, 'month')}"
						 v-for="(day, index) in calendarDays">
						<h6 class="d-flex day-label">
							{{ day.format('D')}}
							<i class="bi bi-check-circle-fill ms-auto" v-if="selectedDate && selectedDate.isSame(day, 'D')"></i>
						</h6>
						<PeerSessionCalendarDay
							class="flex-grow-1"
							@openDetails="args => {dayDetailsData = {day: day, details: args}; dayDetails = true}"
							:sessions="sessions"
							:day="day" :key="day"></PeerSessionCalendarDay>

					</div>
				</div>
				<Transition name="zoom">
					<div class="position-absolute rounded-bottom-3 dayDetail p-3"
						 v-if="dayDetails"
						 style="bottom: 0; height: 100%; width: 100%; z-index: 9999; background: #00000050; backdrop-filter: blur(8px); overflow: scroll">
						<div class="d-flex mb-3">
							<h5 class="mb-0">
								{{ dayDetailsData.day.format("YYYY-MM-DD") }}
							</h5>
							<a role="button" class="ms-auto text-white" @click="dayDetails = false">
								<h5 class="mb-0">
									<i class="bi bi-x-lg"></i>
								</h5>
							</a>
						</div>
						<div class="d-flex flex-column gap-2">
							<div class="p-1 badge text-bg-warning text-start session-list d-flex align-items-center" v-for="s in dayDetailsData.details">
								<div>
									<i class="bi bi-stopwatch me-1"></i>{{ s.timestamps[0].format("HH:mm:ss") }}<i class="bi bi-arrow-right mx-1"></i>{{ s.timestamps[s.timestamps.length - 1].format("HH:mm:ss") }}
								</div>
								<div class="ms-auto">
									<LocaleText t="Duration:"></LocaleText> {{ s.duration.format('HH:mm:ss')}}
								</div>
							</div>

						</div>
					</div>
				</Transition>
			</div>
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

@media screen and (max-width: 992px) {
	.calendar-day{
		min-height: 100px !important;
	}
}

@media screen and (min-width: 992px) {
	.dayDetail{
		display: none;
	}
}

.extra-day .day-label{
	opacity: 0.5;
}
</style>