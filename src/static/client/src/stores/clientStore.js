import {defineStore} from "pinia";
import {ref} from "vue";
import {v4} from "uuid"
import dayjs from "dayjs";


export const clientStore = defineStore('clientStore', () => {
	const notifications = ref([])
	function newNotification(content, status) {
		notifications.value.push({
			id: v4().toString(),
			status: status,
			content: content,
			time: dayjs(),
			show: true
		})
	}
	
	return {
		notifications, newNotification
	}
})