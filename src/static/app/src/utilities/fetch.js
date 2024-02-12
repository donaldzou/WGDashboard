export const fetchGet = async (url, params=undefined, callback=undefined) => {
	const urlSearchParams = new URLSearchParams(params);
	await fetch(`${url}?${urlSearchParams.toString()}`, {
		headers: {
			"content-type": "application/json"
		}
	})
		.then(x => x.json())
		.then(x => callback ? callback(x) : undefined)
		
}

export const fetchPost = async (url, body, callback) => {
	await fetch(`${url}`, {
		headers: {
			"content-type": "application/json"
		},
		method: "POST",
		body: JSON.stringify(body)
	})
		.then(x => x.json())
		.then(x => callback ? callback(x) : undefined)
	// .catch(() => {
	// 	alert("Error occurred! Check console")
	// });
}