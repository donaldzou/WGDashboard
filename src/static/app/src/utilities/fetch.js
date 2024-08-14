import router from "@/router/index.js";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

const getHeaders = () => {
	let headers = {
		"content-type": "application/json"
	}
	const store = DashboardConfigurationStore();
	const apiKey = store.getActiveCrossServer();
	if (apiKey){
		headers['wg-dashboard-apikey'] = apiKey.apiKey
	}
	return headers
}

const getUrl = (url) => {
	const store = DashboardConfigurationStore();
	const apiKey = store.getActiveCrossServer();
	if (apiKey){
		return `${apiKey.host}${url}`
	}
	
	console.log("URL fetching: ", import.meta.env.MODE === 'development' ? url
		: `${window.location.protocol}//${window.location.host}${window.location.pathname}${url}`)
	
	return import.meta.env.MODE === 'development' ? url 
		: `${window.location.protocol}//${window.location.host}${window.location.pathname}${url}`
}

export const fetchGet = async (url, params=undefined, callback=undefined) => {
	const urlSearchParams = new URLSearchParams(params);
	await fetch(`${getUrl(url)}?${urlSearchParams.toString()}`, {
		headers: getHeaders()
	})
	.then((x) => {
		const store = DashboardConfigurationStore();
		if (!x.ok){
			if (x.status !== 200){
				if (x.status === 401){
					
					store.newMessage("WGDashboard", "Session Ended", "warning")
				}
				throw new Error(x.statusText)
			}
		}else{
			return x.json()
		}
	}).then(x => callback ? callback(x) : undefined).catch(x => {
		console.log(x)
			router.push({path: '/signin'})
	})
}

export const fetchPost = async (url, body, callback) => {
	await fetch(`${getUrl(url)}`, {
		headers: getHeaders(),
		method: "POST",
		body: JSON.stringify(body)
	}).then((x) => {
		const store = DashboardConfigurationStore();
		if (!x.ok){
			if (x.status !== 200){
				if (x.status === 401){
					
					store.newMessage("WGDashboard", "Session Ended", "warning")
				}
				throw new Error(x.statusText)
			}
		}else{
			return x.json()
		}
	}).then(x => callback ? callback(x) : undefined).catch(x => {
		console.log(x)
		router.push({path: '/signin'})
	})
}