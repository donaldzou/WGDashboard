export const GetLocale = (key) => {
	if (window.Locale === null)
		return key
	const reg = Object.keys(window.Locale)
	const match = reg.filter(x => {
		return key.match(new RegExp('^' + x + '$', 'gi')) !== null
	})
	if (match.length === 0 || match.length > 1){
		return key
	}
	return key.replace(new RegExp(match[0], 'gi'), window.Locale[match[0]])
}