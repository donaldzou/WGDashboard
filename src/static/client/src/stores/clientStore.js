import {defineStore} from "pinia";
import {onMounted, reactive, ref} from "vue";
import {v4} from "uuid"
import dayjs from "dayjs";
import {axiosGet} from "@/utilities/request.js";


export const clientStore = defineStore('clientStore', () => {
	const notifications = ref([])
	const configurations = ref([])
	const clientProfile = reactive({
		Email: "",
		Profile: {}
	})


	function newNotification(content, status) {
		notifications.value.push({
			id: v4().toString(),
			status: status,
			content: content,
			time: dayjs(),
			show: true
		})
	}

	async function getConfigurations(){
		const data = await axiosGet("/api/configurations")
		if (data){
			configurations.value = data.data
		}else{
			newNotification("Failed to fetch configurations", "danger")
		}
	}
	return {
		notifications, newNotification, getConfigurations, configurations, clientProfile
	}
})