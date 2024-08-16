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

| Parameter  | Type   |   
|------------|--------|   
| `username` | string |   
| `password` | string |   
| `totp`     | string |   


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

### Sign Out

To remove the current session on server side

#### Request

`GET /api/signout`

#### Response

`200 - OK`

```json
{
    "data": null,
    "message": null,
    "status": true
}
```

### Get WireGuard Configurations

To get all WireGuard configurations in `/etc/wireguard`

#### Request

`GET /api/getWireguardConfigurations`

#### Response

`200 - OK`

```json
{
    "data": [
        {
            "Address": "10.200.200.1/24",
            "ConnectedPeers": 0,
            "DataUsage": {
                "Receive": 0.1582,
                "Sent": 2.1012999999999997,
                "Total": 2.2595
            },
            "ListenPort": "51820",
            "Name": "wg0",
            "PostDown": "iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o enp0s1 -j MASQUERADE;",
            "PostUp": "iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o enp0s1 -j MASQUERADE;",
            "PreDown": "",
            "PreUp": "",
            "PrivateKey": "8DsSMli3okgUx5frKbFQ0fMW5ZMyqyxOdOW7+g21L18=",
            "PublicKey": "GQlGi8QJ93hWY7L2xlJyh+7S6+ekER9xP11T92T0O0Q=",
            "SaveConfig": true,
            "Status": false
        }
    ],
    "message": null,
    "status": true
}
```

### Add WireGuard Configuration

Add a new WireGuard Configuration

#### Request

`POST /api/addWireguardConfiguration`

##### Body Parameters

```json
{
    "ConfigurationName": "wg0",
    "Address": "10.0.0.1/24",
    "ListenPort":  51820,
    "PrivateKey": "eJuuamCgakVs2xUZGHh/g7C6Oy89JGh7eE2jjEGbbFc=",
    "PublicKey":  "3Ruirgw9qNRwNpBepkiVjjSe82tY+lDZr6WaFC4wO2g=",
    "PresharedKey": "GMMLKWdJlgsKVoR26BJPsNbDXyfILL+x1Nd6Ecmn4lg=",
    "PreUp":  "",
    "PreDown": "iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o enp0s1 -j MASQUERADE;",
    "PostUp":  "iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o enp0s1 -j MASQUERADE;",
    "PostDown": ""
}
```

| Parameter           | Type   |
|---------------------|--------|
| `ConfigurationName` | string |
| `Address`           | string |
| `ListenPort`        | int    |
| `PrivateKey`        | string |
| `PublicKey`         | string |
| `PresharedKey`      | string |
| `PreUp`             | string |
| `PreDown`           | string |
| `PostUp`            | string |
| `PostDown`          | string |

#### Response

`200 - OK`

If everything is good

```json
{
    "data": null,
    "message": null,
    "status": true
}
```

If the new configuration's `ConfigurationName` is already existed

```json
{
    "data": null,
    "message": "Already have a configuration with the name \"wg0\"",
    "status": false
}
```

If the new configuration's `ListenPort` is used by another configuration

```json
{
    "data": null,
    "message": "Already have a configuration with the port  \"51820\"",
    "status": false
}
```

If the new configuration's `Address` is used by another configuration

```json
{
    "data": null,
    "message": "Already have a configuration with the address  \"10.0.0.1/24\"",
    "status": false
}
```

### Toggle WireGuard Configuration

To turn on/off of a WireGuard Configuration

#### Request

`GET /api/toggleWireguardConfiguration/?configurationName=`

##### Query String Parameter

| Parameter           | Type   |
|---------------------|--------|
| `configurationName` | string |

#### Response

`200 - OK`

If toggle is successful, server will return the current status in `status`: `true` or `false` indicating if the configuration is up or not.

```json
{
    "data": true,
    "message": null,
    "status": true
}
```

If the `configurationName` provided does not exist

```json
{
    "data": null,
    "message": "Please provide a valid configuration name",
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

