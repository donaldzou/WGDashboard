# 📖 API Document for WGDashboard

**Version: v4.0**

**Created by: Donald Zou**

<!-- TOC -->
* [📖 API Document for WGDashboard](#-api-document-for-wgdashboard)
  * [🔑 How to use API Key?](#-how-to-use-api-key)
    * [Create API Key](#create-api-key)
    * [Use API Key](#use-api-key)
  * [API Endpoints](#api-endpoints)
    * [Handshake to Server](#handshake-to-server)
      * [Request](#request)
      * [Response](#response)
    * [Validate Authentication](#validate-authentication)
      * [Request](#request-1)
      * [Response](#response-1)
    * [Authenticate](#authenticate)
      * [Request](#request-2)
        * [Body Parameters](#body-parameters)
      * [Response](#response-2)
    * [Sign Out](#sign-out)
      * [Request](#request-3)
      * [Response](#response-3)
    * [Get WireGuard Configurations](#get-wireguard-configurations)
      * [Request](#request-4)
      * [Response](#response-4)
    * [Add WireGuard Configuration](#add-wireguard-configuration)
      * [Request](#request-5)
        * [Body Parameters](#body-parameters-1)
      * [Response](#response-5)
    * [Toggle WireGuard Configuration](#toggle-wireguard-configuration)
      * [Request](#request-6)
        * [Query String Parameter](#query-string-parameter)
      * [Response](#response-6)
    * [Get WGDashboard Configuration](#get-wgdashboard-configuration)
      * [Request](#request-7)
      * [Response](#response-7)
    * [Update WGDashboard Configuration Item](#update-wgdashboard-configuration-item)
      * [Request](#request-8)
        * [Body Parameters](#body-parameters-2)
      * [Response](#response-8)
    * [Get WGDashboard API Keys](#get-wgdashboard-api-keys)
      * [Request](#request-9)
      * [Response](#response-9)
    * [Add WGDashboard API Key](#add-wgdashboard-api-key)
      * [Request](#request-10)
        * [Body Parameters](#body-parameters-3)
      * [Response](#response-10)
    * [Endpoint](#endpoint)
      * [Request](#request-11)
      * [Response](#response-11)
<!-- TOC -->

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

<hr>

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
<hr>

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

<hr>

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
<hr>

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
<hr>

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
<hr>

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

<hr>

### Get WGDashboard Configuration

Get the WGDashboard Configuration, such as `dashboard_theme`...

#### Request

`GET /api/getDashboardConfiguration`

#### Response

`200 - OK`

```json
{
    "data": {
        "Account": {
            "enable_totp": false,
            "password": "some hashed value :(",
            "totp_verified": false,
            "username": "admin"
        },
        "Database": {
            "type": "sqlite"
        },
        "Other": {
            "welcome_session": false
        },
        "Peers": {
            "peer_display_mode": "grid",
            "peer_endpoint_allowed_ip": "0.0.0.0/0",
            "peer_global_dns": "1.1.1.1",
            "peer_keep_alive": "21",
            "peer_mtu": "1420",
            "remote_endpoint": "192.168.2.38"
        },
        "Server": {
            "app_ip": "0.0.0.0",
            "app_port": "10086",
            "app_prefix": "",
            "auth_req": true,
            "dashboard_api_key": true,
            "dashboard_refresh_interval": "5000",
            "dashboard_sort": "status",
            "dashboard_theme": "dark",
            "version": "v4.0",
            "wg_conf_path": "/etc/wireguard"
        }
    },
    "message": null,
    "status": true
}
```

<hr>

### Update WGDashboard Configuration Item

Update the WGDashboard Configuration one at a time

#### Request

`POST /api/updateDashboardConfigurationItem`

##### Body Parameters

```json
{
    "section": "Server",
    "key": "dashboard_theme",
    "value": "dark"
}
```
| Parameter | Type   |                                                          |
|-----------|--------|----------------------------------------------------------|
| `section` | string | Each section in the `wg-dashboard.ini`                   |
| `key`     | string | Each key/value pair under each in the `wg-dashboard.ini` |
| `value`   | string | Value for this key/value pair                            |


#### Response

`200 - OK`

If update is success

```json
{
    "data": true,
    "message": null,
    "status": true
}
```

If update failed

```json
{
    "data": true,
    "message": "Message related to the error will appear here",
    "status": false
}
```

<hr>

### Get WGDashboard API Keys

Get a list of active API key in WGDashboard

#### Request

`GET /api/getDashboardAPIKeys`

#### Response

`200 - OK`

If API Key function is enabled and there are active API keys

> If `ExpiredAt` is `null`, that means this API key will never expire

```json
{
    "data": [
        {
            "CreatedAt": "2024-08-15 00:42:31",
            "ExpiredAt": null,
            "Key": "AXt1x3TZMukmA-eSnAyESy08I14n20boppSsknHOB-Y"
        },
        {
            "CreatedAt": "2024-08-14 22:50:44",
            "ExpiredAt": "2024-08-21 22:50:43",
            "Key": "ry0Suo0BrypSMzbq0C_TjkEcgrFHHj6UBZGmC2-KI2o"
        }
    ],
    "message": null,
    "status": true
}
```

If API key function is disabled

```json
{
    "data": null,
    "message": "Dashboard API Keys function is disabled",
    "status": false
}
```

<hr>

### Add WGDashboard API Key

Add a new API Key in WGDashboard

#### Request

`POST /api/newDashboardAPIKey`

##### Body Parameters

```json
{
    "neverExpire": false,
    "ExpiredAt": "2024-12-31 16:00:00"
}
```
| Parameter     | Type   |                                                                                   |
|---------------|--------|-----------------------------------------------------------------------------------|
| `neverExpire` | bool   | If this is `false`, please specify a date in `ExpiredAt`                          |
| `ExpiredAt`   | string | If `neverExpire` is `true`, this can be omitted. Format is `YYYY-MM-DD hh:mm:ss`. |

#### Response

`200 - OK`

If success, it will return the latest list of API Keys

```json
{
  "data": [
    {
      "CreatedAt": "2024-08-15 00:42:31",
      "ExpiredAt": null,
      "Key": "AXt1x3TZMukmA-eSnAyESy08I14n20boppSsknHOB-Y"
    },
    {
      "CreatedAt": "2024-08-14 22:50:44",
      "ExpiredAt": "2024-12-31 16:50:43",
      "Key": "ry0Suo0BrypSMzbq0C_TjkEcgrFHHj6UBZGmC2-KI2o"
    }
  ],
  "message": null,
  "status": true
}
```

If API key function is disabled

```json
{
    "data": null,
    "message": "Dashboard API Keys function is disabled",
    "status": false
}
```

<hr>

### Endpoint

Description

#### Request

`GET`

#### Response

`200 - OK`

```json
{
    "data": true,
    "message": null,
    "status": true
}
```

