import router from "@/router/router.js";
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
        if (import.meta.env.MODE === 'development') {
                return url
        }
        // For production builds we construct the URL relative to the current
        // origin. Using `location.pathname` here caused the generated URL to
        // include the current page (e.g. `index.html`), leading to requests
        // like `/index.html/api/...` which the backend does not recognise.
        return `${window.location.origin}${url}`
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
						store.newMessage("WGDashboard", "Sign in session ended, please sign in again", "warning")
					}
					throw new Error(x.statusText)
				}
			}else{
				return x.json()
			}
		})
		.then(x => callback ? callback(x) : undefined).catch(x => {
			console.log("Error:", x)
			// store.newMessage("WGDashboard", `Error: ${x}`, "danger")
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
					store.newMessage("WGDashboard", "Sign in session ended, please sign in again", "warning")
				}
				throw new Error(x.statusText)
			}
		}else{
			return x.json()
		}
	}).then(x => callback ? callback(x) : undefined).catch(x => {
		console.log("Error:", x)
		// store.newMessage("WGDashboard", `Error: ${x}`, "danger")
		router.push({path: '/signin'})
	})
}