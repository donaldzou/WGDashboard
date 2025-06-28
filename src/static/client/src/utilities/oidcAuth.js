export const OIDCAuth = async () => {
	const params = new URLSearchParams(window.location.search)
	const state = params.get('state')
	const code = params.get('code')

}