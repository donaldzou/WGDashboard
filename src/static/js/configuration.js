/**
 * configuration.js - Copyright(C) 2021 Donald Zou [https://github.com/donaldzou]
 * Under Apache-2.0 License
 */


let peers = [];
(function () {
    /**
     * Definitions
     */
    $(".bottomNavConfigs").addClass("active");
    let configuration_name;
    let configuration_interval;
    let configuration_timeout = window.localStorage.getItem("configurationTimeout");
    if (configuration_timeout === null || !["5000", "10000", "30000", "60000"].includes(configuration_timeout)) {
        window.localStorage.setItem("configurationTimeout", "10000");
        configuration_timeout = window.localStorage.getItem("configurationTimeout");
    }
    document.querySelector(`button[data-refresh-interval="${configuration_timeout}"]`).classList.add("active");

    let display_mode = window.localStorage.getItem("displayMode");
    if (display_mode === null || !["grid", "list"].includes(display_mode)) {
        window.localStorage.setItem("displayMode", "grid");
        display_mode = "grid";
    }
    document.querySelectorAll(".display-btn-group button").forEach(ele => ele.classList.remove("active"));
    document.querySelector(`button[data-display-mode="${display_mode}"]`).classList.add("active");

    let $progress_bar = $(".progress-bar");
    let bootstrapModalConfig = {
        keyboard: false,
        backdrop: 'static'
    };
    let addModal = new bootstrap.Modal(document.getElementById('add_modal'), bootstrapModalConfig);
    let deleteBulkModal = new bootstrap.Modal(document.getElementById('delete_bulk_modal'), bootstrapModalConfig);
    let ipModal = new bootstrap.Modal(document.getElementById('available_ip_modal'), bootstrapModalConfig);
    let qrcodeModal = new bootstrap.Modal(document.getElementById('qrcode_modal'), bootstrapModalConfig);
    let settingModal = new bootstrap.Modal(document.getElementById('setting_modal'), bootstrapModalConfig);
    let deleteModal = new bootstrap.Modal(document.getElementById('delete_modal'), bootstrapModalConfig);
    let configurationDeleteModal = new bootstrap.Modal(document.getElementById('configuration_delete_modal'), bootstrapModalConfig);
    let configurationEditModal = new bootstrap.Modal(document.getElementById('editConfigurationModal'), bootstrapModalConfig);
    let peerDataUsageModal = new bootstrap.Modal(document.getElementById('peerDataUsage'), bootstrapModalConfig);
    $("[data-toggle='tooltip']").tooltip();
    $("[data-toggle='popover']").popover();

    /**
     * Chart!!!!!!
     * @type {any}
     */
    let chartUnit = window.localStorage.chartUnit;
    let chartUnitAvailable = ["GB", "MB", "KB"];

    if (chartUnit === null || !chartUnitAvailable.includes(chartUnit)) {
        window.localStorage.setItem("chartUnit", "GB");
        $('.switchUnit[data-unit="GB"]').addClass("active");
    } else {
        $(`.switchUnit[data-unit="${chartUnit}"]`).addClass("active");
    }
    chartUnit = window.localStorage.getItem("chartUnit");


    const totalDataUsageChart = document.getElementById('totalDataUsageChartObj').getContext('2d');
    const totalDataUsageChartObj = new Chart(totalDataUsageChart, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Data Sent',
                data: [],
                stroke: '#FFFFFF',
                borderColor: '#28a745',
                backgroundColor: '#28a7452b',
                pointRadius: 1,
                fill: {target: 'origin'},
                tension: 0,
                borderWidth: 1
            },
            {
                label: 'Data Received',
                data: [],
                stroke: '#FFFFFF',
                borderColor: '#007bff',
                backgroundColor: '#007bff2b',
                pointRadius: 1,
                fill: {target: 'origin'},
                tension: 0,
                borderWidth: 1
            }
            ]
        },
        options: {
            maintainAspectRatio: false,
            showScale: false,
            responsive: false,
            scales: {
                y: {
                    min: 0,
                    ticks: {
                        min: 0,
                        callback: function (value, index, ticks) {
                            return `${value} ${chartUnit}`;
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y} ${chartUnit}`;
                        }
                    }
                }
            }
        }
    });

    let $totalDataUsageChartObj = $("#totalDataUsageChartObj");
    $totalDataUsageChartObj.css("width", "100%");
    totalDataUsageChartObj.width = $totalDataUsageChartObj.parent().width();
    totalDataUsageChartObj.resize();
    $(window).on("resize", function () {
        totalDataUsageChartObj.resize();
    });

    $(".fullScreen").on("click", function () {
        let $chartContainer = $(".chartContainer");
        if ($chartContainer.hasClass("fullScreen")) {
            $(this).children().removeClass("bi-fullscreen-exit").addClass("bi-fullscreen");
            $chartContainer.removeClass("fullScreen");
        } else {
            $(this).children().removeClass("bi-fullscreen").addClass("bi-fullscreen-exit");
            $chartContainer.addClass("fullScreen");
        }
        totalDataUsageChartObj.resize();
    });

    let mul = 1;
    $(".switchUnit").on("click", function () {
        $(".switchUnit").removeClass("active");
        $(`.switchUnit[data-unit=${$(this).data('unit')}]`).addClass("active");
        if ($(this).data('unit') !== chartUnit) {
            switch ($(this).data('unit')) {
                case "GB":
                    if (chartUnit === "MB") {
                        mul = 1 / 1024;
                    }
                    if (chartUnit === "KB") {
                        mul = 1 / 1048576;
                    }
                    break;
                case "MB":
                    if (chartUnit === "GB") {
                        mul = 1024;
                    }
                    if (chartUnit === "KB") {
                        mul = 1 / 1024;
                    }
                    break;
                case "KB":
                    if (chartUnit === "GB") {
                        mul = 1048576;
                    }
                    if (chartUnit === "MB") {
                        mul = 1024;
                    }
                    break;
                default:
                    break;
            }
            window.localStorage.setItem("chartUnit", $(this).data('unit'));
            chartUnit = $(this).data('unit');
            totalDataUsageChartObj.data.datasets[0].data = totalDataUsageChartObj.data.datasets[0].data.map(x => x * mul);
            totalDataUsageChartObj.data.datasets[1].data = totalDataUsageChartObj.data.datasets[1].data.map(x => x * mul);
            totalDataUsageChartObj.update();

            peerDataUsageChartObj.data.datasets[0].data = peerDataUsageChartObj.data.datasets[0].data.map(x => x * mul);
            peerDataUsageChartObj.data.datasets[1].data = peerDataUsageChartObj.data.datasets[1].data.map(x => x * mul);
            peerDataUsageChartObj.update();
        }
    });

    /**
     * Peer Chart
     * @param {Any} response 
     */
    let peerTimePeriod = window.localStorage.peerTimePeriod;
    let peerTimePeriodAvailable = ["30min", "1h", "6h", "24h", "all"];

    if (peerTimePeriod === null || !peerTimePeriodAvailable.includes(peerTimePeriod)) {
        window.localStorage.setItem("peerTimePeriod", "30min");
        $('.switchTimePeriod[data-time="30min"]').addClass("active");
    } else {
        $(`.switchTimePeriod[data-time="${peerTimePeriod}"]`).addClass("active");
    }
    peerTimePeriod = window.localStorage.getItem("peerTimePeriod");


    const peerDataUsageChart = document.getElementById('peerDataUsageChartObj').getContext('2d');
    const peerDataUsageChartObj = new Chart(peerDataUsageChart, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Data Sent',
                data: [],
                stroke: '#FFFFFF',
                borderColor: '#28a745',
                backgroundColor: '#28a7452b',
                pointRadius: 0,
                fill: {target: 'origin'},
                tension: 0,
                borderWidth: 1
            },
            {
                label: 'Data Received',
                data: [],
                stroke: '#FFFFFF',
                borderColor: '#007bff',
                backgroundColor: '#007bff2b',
                pointRadius: 0,
                fill: {target: 'origin'},
                tension: 0,
                borderWidth: 1
            }
            ]
        },
        options: {
            interaction: {
                mode: 'nearest'
            },
            // showLine: false,
            maintainAspectRatio: false,
            showScale: false,
            responsive: false,
            scales: {
                y: {
                    min: 0,
                    ticks: {
                        min: 0,
                        callback: function (value, index, ticks) {
                            return `${value} ${chartUnit}`;
                        }
                    }
                },
                x: {
                    display: false
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y} ${chartUnit}`;
                        }
                    }
                }
            }
        }
    });

    let $peerDataUsageChartObj = $("#peerDataUsageChartObj");
    $peerDataUsageChartObj.css("width", "100%");
    peerDataUsageChartObj.width = $peerDataUsageChartObj.parent().width();
    peerDataUsageChartObj.resize();
    $(window).on("resize", function () {
        peerDataUsageChartObj.resize();
    });

    /**
     * To show alert on the configuration page
     * @param response
     */
    function configurationAlert(response) {
        if (response.listen_port === "" && response.status === "stopped") {
            let configAlert = document.createElement("div");
            configAlert.classList.add("alert");
            configAlert.classList.add("alert-warning");
            configAlert.setAttribute("role", "alert");
            configAlert.innerHTML = 'Peer QR Code and configuration file download required a specified <strong>Listen Port</strong>.';
            document.querySelector("#config_info_alert").appendChild(configAlert);
        }
        if (response.conf_address === "N/A") {
            let configAlert = document.createElement("div");
            configAlert.classList.add("alert");
            configAlert.classList.add("alert-warning");
            configAlert.setAttribute("role", "alert");
            configAlert.innerHTML = 'Configuration <strong>Address</strong> need to be specified to have peers connect to it.';
            document.querySelector("#config_info_alert").appendChild(configAlert);
        }
    }

    function setActiveConfigurationName() {
        $(".nav-conf-link").removeClass("active");
        $(`.sb-${configuration_name}-url`).addClass("active");
    }

    let firstLoading = true;
    $(".nav-conf-link").on("click", function (e) {
        e.preventDefault();
        if (configuration_name !== $(this).data("conf-id")) {
            firstLoading = true;
            $("#config_body").addClass("firstLoading");
            configuration_name = $(this).data("conf-id");
            if (loadPeers($('#search_peer_textbox').val())) {
                setActiveConfigurationName();
                window.history.pushState(null, null, `configuration/${configuration_name}`);
                $("title").text(`${configuration_name} | WGDashboard`);
                $(".index-alert").addClass("d-none").text(``);
                totalDataUsageChartObj.data.labels = [];
                totalDataUsageChartObj.data.datasets[0].data = [];
                totalDataUsageChartObj.data.datasets[1].data = [];
                totalDataUsageChartObj.update();
            }
        }
    });

    /**
     * Parse all responded information onto the configuration header
     * @param response
     */
    function configurationHeader(response) {
        let $conf_status_btn = $(".toggle--switch");

        if (response.checked === "checked") {
            $conf_status_btn.prop("checked", true)
        } else {
            $conf_status_btn.prop("checked", false)
        }
        $conf_status_btn.data("conf-id", configuration_name)


        if (response.running_peer > 0) {
            let d = new Date();
            let time = d.toLocaleString("en-us", { hour: '2-digit', minute: '2-digit', second: "2-digit", hourCycle: 'h23' });
            totalDataUsageChartObj.data.labels.push(`${time}`);

            if (totalDataUsageChartObj.data.datasets[0].data.length === 0) {
                totalDataUsageChartObj.data.datasets[1].lastData = response.total_data_usage[2];
                totalDataUsageChartObj.data.datasets[0].lastData = response.total_data_usage[1];
                totalDataUsageChartObj.data.datasets[0].data.push(0);
                totalDataUsageChartObj.data.datasets[1].data.push(0);
            } else {
                if (totalDataUsageChartObj.data.datasets[0].data.length === 50 && totalDataUsageChartObj.data.datasets[1].data.length === 50) {
                    totalDataUsageChartObj.data.labels.shift();
                    totalDataUsageChartObj.data.datasets[0].data.shift();
                    totalDataUsageChartObj.data.datasets[1].data.shift();
                }

                let newTotalReceive = response.total_data_usage[2] - totalDataUsageChartObj.data.datasets[1].lastData;
                let newTotalSent = response.total_data_usage[1] - totalDataUsageChartObj.data.datasets[0].lastData;
                let k = 0;
                if (chartUnit === "MB") {
                    k = 1024;
                } else if (chartUnit === "KB") {
                    k = 1048576;
                } else {
                    k = 1;
                }
                totalDataUsageChartObj.data.datasets[1].data.push(newTotalReceive * k);
                totalDataUsageChartObj.data.datasets[0].data.push(newTotalSent * k);
                totalDataUsageChartObj.data.datasets[0].lastData = response.total_data_usage[1];
                totalDataUsageChartObj.data.datasets[1].lastData = response.total_data_usage[2];
            }

            totalDataUsageChartObj.update();
        }

        document.querySelector("#conf_name").textContent = configuration_name;
        $("#switch").removeClass("info_loading");
        document.querySelectorAll("#sort_by_dropdown option").forEach(ele => ele.removeAttribute("selected"));
        document.querySelector(`#sort_by_dropdown option[value="${response.sort_tag}"]`).setAttribute("selected", "selected");
        document.querySelector("#conf_status").innerHTML = `${response.status}<span class="dot dot-${response.status}"></span>`;
        document.querySelector("#conf_connected_peers").innerHTML = response.running_peer;
        document.querySelector("#conf_total_data_usage").innerHTML = `${response.total_data_usage[0]} GB`;
        document.querySelector("#conf_total_data_received").innerHTML = `${response.total_data_usage[2]} GB`;
        document.querySelector("#conf_total_data_sent").innerHTML = `${response.total_data_usage[1]} GB`;
        document.querySelector("#conf_public_key").innerHTML = response.public_key;
        document.querySelector("#conf_listen_port").innerHTML = response.listen_port === "" ? "N/A" : response.listen_port;
        document.querySelector("#conf_address").innerHTML = response.conf_address;
        let delay = 0;
        let h6 = $(".info h6");
        for (let i = 0; i < h6.length; i++) {
            setTimeout(function () {
                $(h6[i]).removeClass("info_loading");
            }, delay)
            delay += 40
        }
    }
    /**
     * Parse all responded information onto the peers list
     * @param response
     */
    function configurationPeers(response) {
        let result = "";
        if (response.peer_data.length === 0) {
            document.querySelector(".peer_list").innerHTML = `<div class="col-12" style="text-align: center; margin-top: 1.5rem"><h3 class="text-muted">Oops! No peers found ‘︿’</h3></div>`;
        } else {
            let mode = display_mode === "list" ? "col-12" : "col-sm-6 col-lg-4";
            response.peer_data.forEach(function (peer) {
                let total_r = 0;
                let total_s = 0;
                total_r += peer.cumu_receive;
                total_s += peer.cumu_sent;


                let spliter = '<div class="w-100"></div>';
                let peer_name =
                    `<div class="col-sm peerNameCol">
                        <h5 class="peerName">${peer.name === "" ? "Untitled" : peer.name}</h5>
                        <h6 class="peerLightContainer">
                            <span class="dot dot-${peer.status}" style="margin-left: auto !important;" data-toggle="tooltip" data-placement="left"></span>
                        </h6>
                     </div>`;
                let peer_transfer =
                    `<div class="col-12 peer_data_group" style="">
                        <p class="text-primary" style="">
                            <small><i class="bi bi-arrow-down-right"></i> ${roundN(peer.total_receive + total_r, 4)} GB</small>
                        </p>
                        <p class="text-success">
                            <small><i class="bi bi-arrow-up-right"></i> ${roundN(peer.total_sent + total_s, 4)} GB</small>
                        </p>
                    </div>`;
                let peer_key =
                    `<div class="col-sm">
                        <small class="text-muted" style="display: flex">
                            <strong>PEER</strong>
                            <strong style="margin-left: auto!important; opacity: 0; transition: 0.2s ease-in-out" class="text-primary">CLICK TO COPY</strong>
                        </small>
                        <h6><samp class="ml-auto key">${peer.id}</samp></h6>
                    </div>`;
                let peer_allowed_ip = `
                    <div class="col-sm">
                        <small class="text-muted">
                            <strong>ALLOWED IP</strong>
                        </small>
                        <h6 style="text-transform: uppercase;">${peer.allowed_ip}</h6>
                    </div>`;
                let peer_latest_handshake =
                    `<div class="col-sm">
                        <small class="text-muted"><strong>LATEST HANDSHAKE</strong></small>
                        <h6 style="text-transform: uppercase;">${peer.latest_handshake}</h6>
                    </div>`;
                let peer_endpoint =
                    `<div class="col-sm">
                        <small class="text-muted"><strong>END POINT</strong></small>
                        <h6 style="text-transform: uppercase;">${peer.endpoint}</h6>
                    </div>`;
                let peer_control = `
                    <div class="col-sm">
                        <hr style="margin: 1rem -20px;">
                        <div class="button-group" style="display:flex">
                            <button type="button" class="btn btn-outline-primary btn-setting-peer btn-control" data-peer-id="${peer.id}" data-toggle="modal">
                                <i class="bi bi-gear-fill" data-toggle="tooltip" data-placement="bottom" title="Peer Settings"></i>
                            </button>
                            <button type="button" class="btn btn-outline-primary btn-data-usage-peer btn-control" data-peer-id="${peer.id}" data-toggle="modal">
                                <i class="bi bi-clipboard-data-fill" data-toggle="tooltip" data-placement="bottom" title="Data Usage"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger btn-delete-peer btn-control" data-peer-id="${peer.id}" data-toggle="modal">
                                <i class="bi bi-x-circle-fill" data-toggle="tooltip" data-placement="bottom" title="Delete Peer"></i>
                            </button>
                            
                            <button type="button" class="btn btn-outline-success btn-lock-peer btn-control" data-peer-id="${peer.id}" data-toggle="modal">
                                <i class="bi bi-ethernet" data-toggle="tooltip" data-placement="bottom" data-original-title='Peer enabled. Click to disable peer.' data-peer-name="${peer.name}"></i>
                            </button>`;
                if (peer.private_key !== "") {
                    peer_control +=
                        `<div class="share_peer_btn_group" style="margin-left: auto !important; display: inline">
                            <button type="button" class="btn btn-outline-success btn-qrcode-peer btn-control" data-imgsrc="${global_prefix}qrcode/${response.name}?id=${encodeURIComponent(peer.id)}">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width: 19px;" fill="#28a745"><path d="M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM13 13h2v2h-2zM15 15h2v2h-2zM13 17h2v2h-2zM17 17h2v2h-2zM19 19h2v2h-2zM15 19h2v2h-2zM17 13h2v2h-2zM19 15h2v2h-2z"/></svg>
                            </button>
                            <a href="${global_prefix}download/${response.name}?id=${encodeURIComponent(peer.id)}" class="btn btn-outline-info btn-download-peer btn-control"><i class="bi bi-download"></i></a>
                        </div>`;
                }
                peer_control += '</div></div>';
                let html =
                    `<div class="${mode}" data-id="${peer.id}">
                        <div class="card mb-3 card-${peer.status}">
                            <div class="card-body">
                                <div class="row">` +
                    peer_name +
                    spliter +
                    peer_transfer +
                    peer_key +
                    peer_allowed_ip +
                    peer_latest_handshake +
                    spliter +
                    peer_endpoint +
                    spliter +
                    peer_control +
                    `</div></div></div></div>`;
                result += html;
            });
            response.lock_access_peers.forEach(function (peer) {
                let total_r = 0;
                let total_s = 0;
                total_r += peer.cumu_receive;
                total_s += peer.cumu_sent;
                let spliter = '<div class="w-100"></div>';
                let peer_name =
                    `<div class="col-sm peerNameCol">
                        <h5 class="peerName">${peer.name === "" ? "Untitled" : peer.name}</h5>
                        <h6 class="peerLightContainer"><span class="dot dot-${peer.status}" style="margin-left: auto !important;" data-toggle="tooltip" data-placement="left"></span></h6>
                     </div>`;
                let peer_transfer =
                    `<div class="col-12 peer_data_group" style="">
                        <p class="text-primary" style="">
                            <small><i class="bi bi-arrow-down-right"></i> ${roundN(peer.total_receive + total_r, 4)} GB</small>
                        </p>
                        <p class="text-success">
                            <small><i class="bi bi-arrow-up-right"></i> ${roundN(peer.total_sent + total_s, 4)} GB</small>
                        </p>
                    </div>`;
                let peer_key =
                    `<div class="col-sm">
                        <small class="text-muted" style="display: flex">
                            <strong>PEER</strong><strong style="margin-left: auto!important; opacity: 0; transition: 0.2s ease-in-out" class="text-primary">CLICK TO COPY</strong>
                        </small>
                        <h6><samp class="ml-auto key">${peer.id}/samp></h6>
                    </div>`;
                let peer_allowed_ip =
                    `<div class="col-sm">
                        <small class="text-muted"><strong>ALLOWED IP</strong></small>
                        <h6 style="text-transform: uppercase;">${peer.allowed_ip}</h6>
                    </div>`;
                let peer_latest_handshake =
                    `<div class="col-sm">
                        <small class="text-muted"><strong>LATEST HANDSHAKE</strong></small>
                        <h6 style="text-transform: uppercase;">${peer.latest_handshake}</h6>
                    </div>`;
                let peer_endpoint =
                    `<div class="col-sm">
                        <small class="text-muted"><strong>END POINT</strong></small>
                        <h6 style="text-transform: uppercase;">${peer.endpoint}</h6>
                    </div>`;
                let peer_control = `
                    <div class="col-sm">
                        <hr style="margin: 1rem -20px;">
                        <div class="button-group" style="display:flex; align-items: center;">
                            <button type="button" class="btn btn-outline-success btn-lock-peer btn-control lock" data-peer-id="${peer.id}" data-toggle="modal">
                                <i class="bi bi-ethernet" data-toggle="tooltip" data-placement="bottom" data-original-title='Peer disabled. Click to enable peer.' data-peer-name="${peer.name}"></i>
                            </button>
                            <small class="text-muted" style="margin-left: auto">Peer Disabled</small>
                            </div>`;
                let html = '<div class="' + mode + '" data-id="' + peer.id + '">' +
                    '<div class="card mb-3 card-' + peer.status + '">' +
                    '<div class="card-body">' +
                    '<div class="row">' +
                    peer_name +
                    spliter +
                    peer_transfer +
                    peer_key +
                    peer_allowed_ip +
                    peer_latest_handshake +
                    spliter +
                    peer_endpoint +
                    spliter +
                    peer_control +
                    '</div>' +
                    '</div>' +
                    '</div>' +
                    '</div></div>';
                result += html;
            });
            document.querySelector(".peer_list").innerHTML = result;
            if (configuration_interval === undefined) {
                setConfigurationInterval();
            }
        }
    }

    /**
     * Handle when adding peers by bulk
     */
    function addPeersByBulk() {
        let $new_add_amount = $("#new_add_amount");
        $add_peer.setAttribute("disabled", "disabled");
        $add_peer.innerHTML = `Adding ${$new_add_amount.val()} peers...`;
        let $new_add_DNS = $("#new_add_DNS");
        $new_add_DNS.val(configurations.cleanIp($new_add_DNS.val()));
        let $new_add_endpoint_allowed_ip = $("#new_add_endpoint_allowed_ip");
        $new_add_endpoint_allowed_ip.val(configurations.cleanIp($new_add_endpoint_allowed_ip.val()));
        let $new_add_MTU = $("#new_add_MTU");
        let $new_add_keep_alive = $("#new_add_keep_alive");
        let $enable_preshare_key = $("#enable_preshare_key");
        let data_list = [$new_add_DNS, $new_add_endpoint_allowed_ip, $new_add_MTU, $new_add_keep_alive];
        if ($new_add_amount.val() > 0 && !$new_add_amount.hasClass("is-invalid")) {
            if ($new_add_DNS.val() !== "" && $new_add_endpoint_allowed_ip.val() !== "") {
                let conf = configuration_name;
                let keys = [];
                for (let i = 0; i < $new_add_amount.val(); i++) {
                    keys.push(window.wireguard.generateKeypair());
                }
                $.ajax({
                    method: "POST",
                    url: global_prefix + "add_peer_bulk/" + conf,
                    headers: {
                        "Content-Type": "application/json"
                    },
                    data: JSON.stringify({
                        "DNS": $new_add_DNS.val(),
                        "endpoint_allowed_ip": $new_add_endpoint_allowed_ip.val(),
                        "MTU": $new_add_MTU.val(),
                        "keep_alive": $new_add_keep_alive.val(),
                        "enable_preshared_key": $enable_preshare_key.prop("checked"),
                        "keys": keys,
                        "amount": $new_add_amount.val()
                    }),
                    success: function (response) {
                        if (response !== "true") {
                            $("#add_peer_alert").html(response).removeClass("d-none");
                            data_list.forEach((ele) => ele.removeAttr("disabled"));
                            $add_peer.removeAttribute("disabled");
                            $add_peer.innerHTML = "Save";
                        } else {
                            configurations.loadPeers("");
                            data_list.forEach((ele) => ele.removeAttr("disabled"));
                            $("#add_peer_form").trigger("reset");
                            $add_peer.removeAttribute("disabled");
                            $add_peer.innerHTML = "Save";
                            configurations.showToast($new_add_amount.val() + " peers added successful!");
                            configurations.addModal().toggle();
                        }
                    }
                });
            } else {
                $("#add_peer_alert").html("Please fill in all required box.").removeClass("d-none");
                $add_peer.removeAttribute("disabled");
                $add_peer.innerHTML = "Add";
            }
        } else {
            $add_peer.removeAttribute("disabled");
            $add_peer.innerHTML = "Add";
        }
    }

    /**
     * Delete one peer or by bulk
     * @param config
     * @param peer_ids
     */
    function deletePeers(config, peer_ids) {
        $.ajax({
            method: "POST",
            url: global_prefix + "remove_peer/" + config,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({ "action": "delete", "peer_ids": peer_ids }),
            success: function (response) {
                if (response !== "true") {
                    if (configurations.deleteModal()._isShown) {
                        $("#remove_peer_alert").html(response + $("#add_peer_alert").html())
                            .removeClass("d-none");
                        $("#delete_peer").removeAttr("disabled").html("Delete");
                    }
                    if (configurations.deleteBulkModal()._isShown) {
                        let $bulk_remove_peer_alert = $("#bulk_remove_peer_alert");
                        $bulk_remove_peer_alert.html(response + $bulk_remove_peer_alert.html())
                            .removeClass("d-none");
                        $("#confirm_delete_bulk_peers").removeAttr("disabled").html("Delete");
                    }
                } else {
                    if (configurations.deleteModal()._isShown) {
                        configurations.deleteModal().toggle();
                    }
                    if (configurations.deleteBulkModal()._isShown) {
                        $("#confirm_delete_bulk_peers").removeAttr("disabled").html("Delete");
                        $("#selected_peer_list").html('');
                        $(".delete-bulk-peer-item.active").removeClass('active');
                        configurations.deleteBulkModal().toggle();
                    }
                    configurations.loadPeers($('#search_peer_textbox').val());
                    configurations.showToast(`Deleted ${peer_ids.length} peers`)
                    $("#delete_peer").removeAttr("disabled").html("Delete");
                }
            }
        });
    }

    /**
     * Handle when the server is not responding
     */
    function noResponding(message = "Opps! <br> I can't connect to the server.") {
        document.querySelectorAll(".no-response").forEach(ele => ele.classList.add("active"));
        setTimeout(function () {
            document.querySelectorAll(".no-response").forEach(ele => ele.classList.add("show"));
            document.querySelector("#right_body").classList.add("no-responding");
            document.querySelector(".navbar").classList.add("no-responding");
            document.querySelector(".no-response .container h4").innerHTML = message;
        }, 10);
    }

    /**
     * Remove no responding
     */
    function removeNoResponding() {
        document.querySelectorAll(".no-response").forEach(ele => ele.classList.remove("show"));
        document.querySelector("#right_body").classList.remove("no-responding");
        document.querySelector(".navbar").classList.remove("no-responding");
        setTimeout(function () {
            document.querySelectorAll(".no-response").forEach(ele => ele.classList.remove("active"));
        }, 1010);
    }

    /**
     * Set configuration refresh Interval
     */
    function setConfigurationInterval() {
        configuration_interval = setInterval(function () {
            loadPeers($('#search_peer_textbox').val());
        }, configuration_timeout);
    }

    /**
     * Remove configuration refresh interval
     */
    function removeConfigurationInterval() {
        clearInterval(configuration_interval);
    }

    /**
     * Start Progress Bar
     */
    function startProgressBar() {
        $progress_bar.css("width", "0%")
            .css("opacity", "100")
            .css("background", "rgb(255,69,69)")
            .css("background",
                "linear-gradient(145deg, rgba(255,69,69,1) 0%, rgba(0,115,186,1) 100%)")
            .css("width", "25%");
        setTimeout(function () {
            stillLoadingProgressBar();
        }, 300);
    }

    /**
     * Still Loading Progress Bar
     */
    function stillLoadingProgressBar() {
        $progress_bar.css("transition", "3s ease-in-out").css("width", "75%");
    }

    /**
     * End Progress Bar
     */
    function endProgressBar() {
        $progress_bar.css("transition", "0.3s ease-in-out").css("width", "100%");
        setTimeout(function () {
            $progress_bar.css("opacity", "0");
        }, 250);
    }

    /**
     * Round Transfer number into 4 digits
     * @param value
     * @param digits
     * @returns {number}
     */
    function roundN(value, digits) {
        let tenToN = 10 ** digits;
        return (Math.round(value * tenToN)) / tenToN;
    }

    /**
     * Load Peers from server to configuration page
     * @param searchString
     */
    let time = 0;
    let count = 0;
    let d1 = new Date();

    function loadPeers(searchString) {
        d1 = new Date();
        let good = true;
        $.ajax({
            method: "GET",
            url: `${global_prefix}get_config/${configuration_name}?search=${encodeURIComponent(searchString)}`,
            headers: { "Content-Type": "application/json" }
        }).done(function (response) {
            console.log(response);
            parsePeers(response);
        }).fail(function () {
            noResponding();
            good = false;
        });
        return good;
    }

    function parsePeers(response) {
        if (response.status) {
            removeAllTooltips();
            let d2 = new Date();
            let seconds = (d2 - d1);
            time += seconds;
            count += 1;
            window.console.log(`Average time: ${time / count}ms`);
            $("#peer_loading_time").html(`Peer Loading Time: ${seconds}ms`);
            removeNoResponding();
            peers = response.data.peer_data;
            configurationAlert(response.data);
            configurationHeader(response.data);
            configurationPeers(response.data);

            $(".dot.dot-running").attr("title", "Peer Connected").tooltip();
            $(".dot.dot-stopped").attr("title", "Peer Disconnected").tooltip();
            $("i[data-toggle='tooltip']").tooltip();
            $("#configuration_name").text(configuration_name);
            if (firstLoading) {
                firstLoading = false;
                $("#config_body").removeClass("firstLoading");
            }
        } else {
            noResponding(response.message);
            removeConfigurationInterval();
        }
    }

    function removeAllTooltips() {
        $(".tooltip").remove();
    }

    function toggleAccess(peerID) {
        $.ajax({
            url: "${global_prefix}api/togglePeerAccess",
            method: "POST",
            headers: { "Content-Type": "application/json" },
            data: JSON.stringify({ "peerID": peerID, "config": configuration_name })
        }).done(function (res) {
            if (res.status) {
                loadPeers($('#search_peer_textbox').val());
            } else {
                showToast(res.reason);
            }
        });
    }

    /**
     * Generate Private and Public key for a new peer
     */
    function generate_key() {
        let keys = window.wireguard.generateKeypair();
        document.querySelector("#private_key").value = keys.privateKey;
        document.querySelector("#public_key").value = keys.publicKey;
        document.querySelector("#add_peer_alert").classList.add("d-none");
        document.querySelector("#re_generate_key i").classList.remove("rotating");
        document.querySelector("#enable_preshare_key").value = keys.presharedKey;
    }

    /**
     * Show toast
     * @param msg
     */
    let numberToast = 0;
    function showToast(msg) {
        $(".toastContainer").append(
            `<div id="${numberToast}-toast" class="toast hide" role="alert" data-delay="5000">
				<div class="toast-header">
					<strong class="mr-auto">WGDashboard</strong>
					<button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				<div class="toast-body">${msg}</div>
				<div class="toast-progressbar"></div>
			</div>` )
        $(`#${numberToast}-toast`).toast('show');
        $(`#${numberToast}-toast .toast-body`).html(msg);
        $(`#${numberToast}-toast .toast-progressbar`).css("transition", `width ${$(`#${numberToast}-toast .toast-progressbar`).parent().data('delay')}ms cubic-bezier(0, 0, 0, 0)`);
        $(`#${numberToast}-toast .toast-progressbar`).css("width", "0px");
        numberToast++;
    }

    /**
     * Update peer's refresh interval
     * @param res
     * @param interval
     */
    function updateRefreshInterval(interval) {
        configuration_timeout = interval;
        window.localStorage.setItem("configurationTimeout", configuration_timeout.toString());
        removeConfigurationInterval();
        setConfigurationInterval();
        showToast("Refresh Interval set to " + Math.round(interval / 1000) + " seconds");
    }

    /**
     * Clean IP
     * @param val
     * @returns {string}
     */
    function cleanIp(val) {
        let clean_ip = val.split(',');
        for (let i = 0; i < clean_ip.length; i++) {
            clean_ip[i] = clean_ip[i].trim(' ');
        }
        return clean_ip.filter(Boolean).join(",");
    }

    /**
     * Trigger IP badge and item
     * @param ip
     */
    function trigger_ip(ip) {
        let $ip_ele = document.querySelector(`.available-ip-item[data-ip='${ip}']`);
        if ($ip_ele) {
            if ($ip_ele.classList.contains("active")) {
                $ip_ele.classList.remove("active");
                document.querySelector(`#selected_ip_list .badge[data-ip='${ip}']`).remove();
            } else {
                $ip_ele.classList.add("active");
                document.querySelector("#selected_ip_list").innerHTML += `<span class="badge badge-primary available-ip-badge" style="cursor: pointer" data-ip="${ip}">${ip}</span>`;
            }
        }
    }

    /**
     * Download single configuration file
     * @param conf
     */
    function download_one_config(conf) {
        let link = document.createElement('a');
        link.download = conf.filename;
        let blob = new Blob([conf.content], { type: 'text/conf' });
        link.href = window.URL.createObjectURL(blob);
        link.click();
    }

    /**
     * Toggle delete by bulk IP
     * @param element
     */
    function toggleBulkIP(element) {
        let $selected_peer_list = $("#selected_peer_list");
        let id = element.data("id");
        let name = element.data("name") === "" ? "Untitled Peer" : element.data("name");
        if (element.hasClass("active")) {
            element.removeClass("active");
            $("#selected_peer_list .badge[data-id='" + id + "']").remove();
        } else {
            element.addClass("active");
            $selected_peer_list.append('<span class="badge badge-danger delete-peer-bulk-badge" style="cursor: pointer; text-overflow: ellipsis; max-width: 100%; overflow-x: hidden" data-id="' + id + '">' + name + ' - ' + id + '</span>');
        }
    }

    /**
     * Copy public keys to clipboard
     * @param element
     */
    function copyToClipboard(element) {
        let $temp = $("<input>");
        $body.append($temp);
        $temp.val($(element).text()).trigger("select");
        document.execCommand("copy");
        $temp.remove();
    }

    /**
     * Get all available IP for this configuration
     */
    function getAvailableIps() {
        $.ajax({
            "url": `${global_prefix}available_ips/${configuration_name}`,
            "method": "GET",
        }).done(function (res) {
            if (res.status === true) {
                available_ips = res.data;
                let $list_group = document.querySelector("#available_ip_modal .modal-body .list-group");
                $list_group.innerHTML = "";
                document.querySelector("#allowed_ips").value = available_ips[0];
                available_ips.forEach((ip) =>
                    $list_group.innerHTML +=
                    `<a class="list-group-item list-group-item-action available-ip-item" style="cursor: pointer" data-ip="${ip}">${ip}</a>`);
            } else {
                document.querySelector("#allowed_ips").value = res.message;
                document.querySelector("#search_available_ip").setAttribute("disabled", "disabled");
            }
        });
    }

    function getConfigurationDetails() {
        function done(res){
            console.log(res);
        }
        ajaxGetJSON(`${global_prefix}api/getConfigurationInfo?configName=${configuration_name}`, done)
    }

    configurations = {
        peerDataUsageChartObj: () => { return peerDataUsageChartObj },
        peerDataUsageModal: () => { return peerDataUsageModal },
        addModal: () => { return addModal; },
        deleteBulkModal: () => { return deleteBulkModal; },
        deleteModal: () => { return deleteModal; },
        configurationDeleteModal: () => { return configurationDeleteModal; },
        ipModal: () => { return ipModal; },
        qrcodeModal: () => { return qrcodeModal; },
        settingModal: () => { return settingModal; },
        configurationEditModal: () => { return configurationEditModal; },
        configurationTimeout: () => { return configuration_timeout; },
        updateDisplayMode: () => { display_mode = window.localStorage.getItem("displayMode"); },
        removeConfigurationInterval: () => { removeConfigurationInterval(); },

        loadPeers: (searchString) => { loadPeers(searchString); },
        addPeersByBulk: () => { addPeersByBulk(); },
        deletePeers: (config, peers_ids) => { deletePeers(config, peers_ids); },
        deleteConfiguration: () => { deleteConfiguration() },
        parsePeers: (response) => { parsePeers(response); },
        toggleAccess: (peerID) => { toggleAccess(peerID); },

        getConfigurationDetails: () => { getConfigurationDetails() },
        setConfigurationName: (confName) => { configuration_name = confName; },
        getConfigurationName: () => { return configuration_name; },
        setActiveConfigurationName: () => { setActiveConfigurationName(); },
        getAvailableIps: () => { getAvailableIps(); },
        generateKeyPair: () => { generate_key(); },
        showToast: (message) => { showToast(message); },
        updateRefreshInterval: (interval) => { updateRefreshInterval(interval); },
        copyToClipboard: (element) => { copyToClipboard(element); },
        toggleDeleteByBulkIP: (element) => { toggleBulkIP(element); },
        downloadOneConfig: (conf) => { download_one_config(conf); },
        triggerIp: (ip) => { trigger_ip(ip); },
        cleanIp: (val) => { return cleanIp(val); },
        startProgressBar: () => { startProgressBar(); },
        stillLoadingProgressBar: () => { stillLoadingProgressBar(); },
        endProgressBar: () => { endProgressBar(); }
    };
})();
