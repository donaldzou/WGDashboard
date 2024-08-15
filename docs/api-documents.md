# 📖 API Document for WGDashboard

**Version: v4.0**

**Created by: Donald Zou**

<hr>

## 🔑 How to use API Key?

### Create API Key

1. To request an API Key, simply login to your WGDashboard, go to **Settings**, scroll to the very bottom. Click the **switch** on the right to enable API Key.
2. Click the blur **Create** button, set an **expiry date** you want or **never expire**, then click **Done**.

### Use API Key

- Simply add `wg-dashboard-apikey` with the value of your API key into the HTTP Header.

```javascript
fetch('http://server:10086/api/handshake', {
    headers: {
       'content-type': 'application/json',
        'wg-dashboard-apikey': 'insert your api key here'
    },
    method: "GET"
})
```

## API Endpoints

### Handshake to Server

This endpoint is designed for a simple handshake when using API key to connect. If `status` is `true` that means 

#### Request

`GET /api/handshake`

#### Response

`200 - OK`

```json
{
    "data": null,
    "message": null,
    "status": true
}
```

`401 - UNAUTHORIZED`

```json
{
    "data": null,
    "message": "Unauthorized access.",
    "status": false
}
```
> Notice: this `401` response will return at all endpoint if your API Key or session is invalid.

### Validate Authentication

This endpoint if needed for non-cross-server access. This will check if the cookie on the client side is still valid on the server side.

#### Request

`GET /api/validateAuthentication`

#### Response

`200 - OK`

Session is still valid

```json
{
    "data": null,
    "message": null,
    "status": true
}
```

Session is invalid

```json
{
    "data": null,
    "message": "Invalid authentication.",
    "status": false
}
```

### Authenticate

This endpoint is dedicated for non-cross-server access. It is used to authenticate user's username, password and TOTP 

#### Request

`POST /api/authenticate`

##### Body Parameters

```json
{
    "username": "admin",
    "password": "admin",
    "totp": "123456"
}
```

**`username`** string

**`password`** string

**`totp`** string

#### Response

`200 - OK`

If username, password and TOTP matched

```json
{
    "data": null,
    "message": null,
    "status": true
}
```

If username, password or TOTP is not match

```json
{
    "data": null,
    "message": "Sorry, your username, password or OTP is incorrect.",
    "status": false
}
```





=============

### Endpoint

Description

#### Request

`GET`

#### Response

`200 - OK`

```json

```

