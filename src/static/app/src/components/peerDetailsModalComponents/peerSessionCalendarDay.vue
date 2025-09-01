<script setup lang="ts">
import {computed} from "vue";

const props = defineProps(['sessions', 'day'])
import dayjs from "dayjs";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore"
import duration from "dayjs/plugin/duration"
import LocaleText from "@/components/text/localeText.vue";
dayjs.extend(isSameOrBefore)
dayjs.extend(duration)

const sessionsOfToday = computed(() => {
	let sessions = props.sessions.map(x => dayjs(x)).filter(x => x.isSame(props.day, 'D')).reverse()
	let result = []
	if (sessions.length > 1){
		let cur = [sessions[0]]
		for (let s of sessions.slice(1)){
			if (s.isSameOrBefore(cur[cur.length - 1].add(3, 'minute'))){
				cur.push(s)
			}else{
				result.push({
					timestamps: cur,
					duration: dayjs.duration(
						cur[cur.length - 1].diff(cur[0])
					)
				})
				cur = [s]
			}

		}
		result.push({
			timestamps: cur,
			duration: dayjs.duration(
				cur[cur.length - 1].diff(cur[0])
			)
		})
	}
	return result
})

defineEmits(['openDetails'])
</script>

<template>
<div class="d-flex gap-1 flex-column session-list" @click="$emit('openDetails', sessionsOfToday)">
	<small v-if="sessionsOfToday.length > 0" class="sessions-label">
		<LocaleText :t="sessionsOfToday.length + ' Session' + (sessionsOfToday.length > 1 ? 's':'')"></LocaleText>
	</small>
	<div class="d-flex flex-wrap gap-1 session-dot">
		<div class="bg-warning"
			 style="height: 5px; width: 5px; border-radius: 100%; vertical-align: top" v-for="_ in sessionsOfToday.length"></div>
	</div>
	<div class="p-1 badge text-bg-warning text-start session-badge-list" v-for="s in sessionsOfToday">
		<div>
			<i class="bi bi-stopwatch me-1"></i>{{ s.timestamps[0].format("HH:mm:ss") }}<i class="bi bi-arrow-right mx-1"></i>{{ s.timestamps[s.timestamps.length - 1].format("HH:mm:ss") }}
		</div>
		<div class="mt-1">
			<LocaleText t="Duration:"></LocaleText> {{ s.duration.format('HH:mm:ss')}}
		</div>
	</div>
</div>
</template>

<style scoped>
@media screen and (max-width: 992px) {
	.calendar-day .session-badge-list{
		display: none;
	}

	.sessions-label{
		display: none;
	}
}
.session-list{
	aspect-ratio: 1 / 1;
}
@media screen and (min-width: 992px) {
	.session-dot{
		display: none !important;
	}

	.session-list{
		height: calc(100vh / 8);
		overflow: scroll;
		aspect-ratio: auto !important;
	}
}



</style>