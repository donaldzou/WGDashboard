# 📖 API Document for WGDashboard

**Version: v4.0**

**Created by: Donald Zou**

<hr>

## 🔑 How to use API Key?

### Create API Key

1. To request an API Key, simply login to your WGDashboard, go to **Settings**, scroll to the very bottom. Click the **switch** on the right to enable API Key.
2. Click the blur **Create** button, set an **expiry date** you want or **never expire**, then click **Done**.

### Use API Key in `fetch()`

```javascript
fetch('http://server:10086', {
    headers: {
       'content-type': 'application/json',
        'wg-dashboard-apikey': 'insert your api key here'
    }
})
```
To use API Key, simply insert `wg-dashboard-apikey` with the value of your API key into the `header` in your http request.
