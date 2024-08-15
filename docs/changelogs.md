# ⏰ Changelogs of WGDashboard

#### v3.0.0 - v3.0.6.2 - Jan 18, 2022

- 🎉  **New Features**
    - **Moved from TinyDB to SQLite**: SQLite provide a better performance and loading speed when getting peers! Also avoided crashing the database due to **race condition**.
    - **Added Gunicorn WSGI Server**: This could provide more stable on handling HTTP request, and more flexibility in the future (such as HTTPS support). **BIG THANKS to @pgalonza :heart:**
    - **Add Peers by Bulk:** User can add peers by bulk, just simply set the amount and click add.
    - **Delete Peers by Bulk**: User can delete peers by bulk, without deleting peers one by one.
    - **Download Peers in Zip**: User can download all *downloadable* peers in a zip.
    - **Added Pre-shared Key to peers:** Now each peer can add with a pre-shared key to enhance security. Previously added peers can add the pre-shared key through the peer setting button.
    - **Redirect Back to Previous Page:** The dashboard will now redirect you back to your previous page if the current session got timed out and you need to sign in again.
    - **Added Some [🥘 Experimental Functions](#-experimental-functions)**

- 🪚  **Bug Fixed**
    - [IP Sorting range issues #99](https://github.com/donaldzou/WGDashboard/issues/99) [❤️ @barryboom]
    - [INvalid character written to tunnel json file #108](https://github.com/donaldzou/WGDashboard/issues/108) [❤️ @ikidd]
    - [Add IPv6 #91](https://github.com/donaldzou/WGDashboard/pull/91) [❤️ @pgalonza]
    - [Added MTU and PersistentKeepalive to QR code and download files #112](https://github.com/donaldzou/WGDashboard/pull/112) [:heart: @reafian]
    - **And many other bugs provided by our beloved users** :heart:
- **🧐  Other Changes**
    - **Key generating moved to front-end**: No longer need to use the server's WireGuard to generate keys, thanks to the `wireguard.js` from the [official repository](https://git.zx2c4.com/wireguard-tools/tree/contrib/keygen-html/wireguard.js)!
    - **Peer transfer calculation**: each peer will now show all transfer amount (previously was only showing transfer amount from the last configuration start-up).
    - **UI adjustment on running peers**: peers will have a new style indicating that it is running.
    - **`wgd.sh` finally can update itself**: So now user could update the whole dashboard from `wgd.sh`, with the `update` command.
    - **Minified JS and CSS files**: Although only a small changes on the file size, but I think is still a good practice to save a bit of bandwidth ;)

*And many other small changes for performance and bug fixes! :laughing:*

#### v2.3.1 - Sep 8, 2021

- Updated dashboard's name to **WGDashboard**!!

#### v2.3 - Sep 8, 2021

- 🎉  **New Features**
    - **Update directly from `wgd.sh`:** Now you can update WGDashboard directly from the bash script.
    - **Displaying Peers:** You can switch the display mode between list and table in the configuration page.
- 🪚  **Bug Fixed**
    - [Peer DNS Validation Fails #67](issues/67): Added DNS format check. [❤️ @realfian]
    - [configparser.NoSectionError: No section: 'Interface' #66](issues/66): Changed permission requirement for `etc/wireguard` from `744` to `755`. [❤️ @ramalmaty]
    - [Feature request: Interface not loading when information missing #73](issues/73): Fixed when Configuration Address and Listen Port is missing will crash the dashboard. [❤️ @js32]
    - [Remote Peer, MTU and PersistentKeepalives added #70](pull/70): Added MTU, remote peer and Persistent Keepalive. [❤️ @realfian]
    - [Fixes DNS check to support search domain #65](pull/65): Added allow input domain into DNS. [❤️@davejlong]
- **🧐  Other Changes**
    - Moved Add Peer Button into the right bottom corner.

#### v2.2.1 - Aug 16, 2021

Bug Fixed:
- Added support for full subnet on Allowed IP
- Peer setting Save button

#### v2.2 - Aug 14, 2021

- 🎉  **New Features**
    - **Add new peers**: Now you can add peers directly on dashboard, it will generate a pair of private key and public key. You can also set its DNS, endpoint allowed IPs. Both can set a default value in the setting page. [❤️ in [#44](https://github.com/donaldzou/wireguard-dashboard/issues/44)]
    - **QR Code:** You can add the private key in peer setting of your existed peer to create a QR code. Or just create a new one, dashboard will now be able to auto generate a private key and public key ;) Don't worry, all keys will be generated on your machine, and **will delete all key files after they got generated**. [❤️ in [#29](https://github.com/donaldzou/wireguard-dashboard/issues/29)]
    - **Peer configuration file download:** Same as QR code, you now can download the peer configuration file, so you don't need to manually input all the details on the peer machine! [❤️ in [#40](https://github.com/donaldzou/wireguard-dashboard/issues/40)]
    - **Search peers**: You can now search peers by their name.
    - **Autostart on boot:** Added a tutorial on how to start the dashboard to on boot! Please read the [tutorial below](#autostart-wireguard-dashboard-on-boot). [❤️ in [#29](https://github.com/donaldzou/wireguard-dashboard/issues/29)]
    - **Click to copy**: You can now click and copy all peer's public key and configuration's public key.
    - ....
- 🪚  **Bug Fixed**
    - When there are comments in the wireguard config file, will cause the dashboard to crash.
    - Used regex to search for config files.
- **🧐  Other Changes**
    - Moved all external CSS and JavaScript file to local hosting (Except Bootstrap Icon, due to large amount of SVG files).
    - Updated Python dependencies
        - Flask: `v1.1.2 => v2.0.1`
        - Jinja: `v2.10.1 => v3.0.1`
        - icmplib: `v2.1.1 => v3.0.1`
    - Updated CSS/JS dependencies
        - Bootstrap: `v4.5.3 => v4.6.0`
    - UI adjustment
        - Adjusted how peers will display in larger screens, used to be 1 row per peer, now is 3 peers in 1 row.

#### v2.1 - Jul 2, 2021

- Added **Ping** and **Traceroute** tools!
- Adjusted the calculation of data usage on each peers
- Added refresh interval of the dashboard
- Bug fixed when no configuration on fresh install ([#23](https://github.com/donaldzou/wireguard-dashboard/issues/23))
- Fixed crash when too many peers ([#22](https://github.com/donaldzou/wireguard-dashboard/issues/22))

#### v2.0 - May 5, 2021

- Added login function to dashboard
    - ***I'm not using the most ideal way to store the username and password, feel free to provide a better way to do this if you any good idea!***
- Added a config file to the dashboard
- Dashboard config can be change within the **Setting** tab on the side bar
- Adjusted UI
- And much more!

#### v1.1.2 - Apr 3, 2021

- Resolved issue [#3](https://github.com/donaldzou/wireguard-dashboard/issues/3).

#### v1.1.1 - Apr 2, 2021

- Able to add a friendly name to each peer. Thanks [#2](https://github.com/donaldzou/wireguard-dashboard/issues/2) !

#### v1.0 - Dec 27, 2020

- Added the function to remove peers