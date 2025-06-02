export const requestURl = (url) => {
	return import.meta.env.MODE === 'development' ? '/client' + url
		: `${window.location.protocol}//${(window.location.host + window.location.pathname + url).replace(/\/\//g, '/')}`
}

