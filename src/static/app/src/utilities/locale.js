export const GetLocale = (key) => {
	console.log(key)
	
	if (window.Locale === null)
		return key
	
	const reg = Object.keys(window.Locale)
	const match = reg.filter(x => {
		return key.match(new RegExp('^' + x + '$', 'g')) !== null
	})
	console.log(match)
	if (match.length === 0 || match.length > 1){
		return key
	}
	return window.Locale[match[0]]
}