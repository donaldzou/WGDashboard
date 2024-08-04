import router from "@/router/index.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
export const fetchGet = async (url, params=undefined, callback=undefined) => {
	const urlSearchParams = new URLSearchParams(params);
	await fetch(`${url}?${urlSearchParams.toString()}`, {
		headers: {
			"content-type": "application/json"
		}
	})
	.then((x) => {
		const store = DashboardConfigurationStore();
		if (!x.ok){
			if (x.status !== 200){
				if (x.status === 401){
					router.push({path: '/signin'})
					store.newMessage("WGDashboard", "Session Ended", "warning")
				}
				throw new Error(x.statusText)
			}
		}else{
			return x.json()
		}
	}).then(x => callback ? callback(x) : undefined).catch(x => {
		console.log(x)
	})
}

export const fetchPost = async (url, body, callback) => {
	await fetch(`${url}`, {
		headers: {
			"content-type": "application/json"
		},
		method: "POST",
		body: JSON.stringify(body)
	}).then((x) => {
		const store = DashboardConfigurationStore();
		if (!x.ok){
			if (x.status !== 200){
				if (x.status === 401){
					router.push({path: '/signin'})
					store.newMessage("WGDashboard", "Session Ended", "warning")
				}
				throw new Error(x.statusText)
			}
		}else{
			return x.json()
		}
	}).then(x => callback ? callback(x) : undefined).catch(x => {
		console.log(x)
	})
}