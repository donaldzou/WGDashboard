import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";

export const GetLocale = (key) => {
	const store = DashboardConfigurationStore()
	
	if (store.Locale === null)
		return key
	const reg = Object.keys(store.Locale)
	const match = reg.filter(x => {
		return key.match(new RegExp('^' + x + '$', 'gi')) !== null
	})
	if (match.length === 0 || match.length > 1){
		return key
	}
	return key.replace(new RegExp(match[0], 'gi'), store.Locale[match[0]])
}