import {defineStore} from "pinia";
import {onMounted, reactive, ref} from "vue";
import {v4} from "uuid"
import dayjs from "dayjs";
import {axiosGet} from "@/utilities/request.js";


export const clientStore = defineStore('clientStore',  {
	state: () => ({
		notifications: [],
		configurations: [],
		clientProfile: {
			Email: "",
			Profile: {}
		}
	}),
	actions: {
		newNotification(content, status){
			this.notifications.push({
				id: v4().toString(),
				status: status,
				content: content,
				time: dayjs(),
				show: true
			})
		},
		async getClientProfile(){
			const data = await axiosGet('/api/settings/getClientProfile')
			if (data){
				this.clientProfile.Profile = data.data
			}else{
				this.newNotification("Failed to fetch client profile", "danger")
			}
		},
		async getConfigurations(){
			const data = await axiosGet("/api/configurations")
			if (data){
				this.configurations = data.data
				this.configurations.forEach(c => {
					console.log(
						c.jobs.sort((x, y) => {
							if (dayjs(x.CreationDate).isBefore(y.CreationDate)){
								return 1
							}else if (dayjs(x.CreationDate).isAfter(y.CreationDate)){
								return -1
							}else{
								return 0
							}
						})

					)
					console.log(c.jobs.find(x => x.Field === 'date'))
				})
			}else{
				this.newNotification("Failed to fetch configurations", "danger")
			}
		}
	}
})