let $body = $("body");
let available_ips = [];
let $add_peer = document.getElementById("save_peer");

$("#configuration_delete").on("click", function(){
    configurations.configurationDeleteModal().toggle();
});

function ajaxPostJSON(url, data, doneFunc){
    $.ajax({
        url: url,
        method: "POST",
        data: JSON.stringify(data),
        headers: {"Content-Type": "application/json"}
    }).done(function (res) { 
        doneFunc(res);
    });
}

function ajaxGetJSON(url, doneFunc){
    $.ajax({
        url: url,
        headers: {"Content-Type": "application/json"}
    }).done(function (res) { 
        doneFunc(res);
    });
}

$("#sure_delete_configuration").on("click", function () {
    configurations.removeConfigurationInterval();
    let ele = $(this)
    ele.attr("disabled", "disabled");
    function done(res){
        if (res.status){
            $('#configuration_delete_modal button[data-dismiss="modal"]').remove();
            ele.text("Delete Successful! Redirecting in 5 seconds.");
            setTimeout(function(){
                window.location.replace('/');
            }, 5000)
        }else{
            $("#remove_configuration_alert").removeClass("d-none").text(res.reason);
        }
    }
    ajaxPostJSON("/api/deleteConfiguration", {"name": configurations.getConfigurationName()}, done);
});

function loadPeerDataUsageChartDone(res){
    if (res.status === true){
        let t = new Date();
        let string = `${t.getDate()}/${t.getMonth()}/${t.getFullYear()} ${t.getHours() > 10 ? t.getHours():`0${t.getHours()}`}:${t.getMinutes() > 10 ? t.getMinutes():`0${t.getMinutes()}`}:${t.getSeconds() > 10 ? t.getSeconds():`0${t.getSeconds()}`}`;
        $(".peerDataUsageUpdateTime").html(`Updated on: ${string}`);

        configurations.peerDataUsageChartObj().data.labels = [];
        configurations.peerDataUsageChartObj().data.datasets[0].data = [];
        configurations.peerDataUsageChartObj().data.datasets[1].data = [];
        console.log(res);
        let data = res.data;
        configurations.peerDataUsageChartObj().data.labels.push(data[data.length - 1].time);
        configurations.peerDataUsageChartObj().data.datasets[0].data.push(0);
        configurations.peerDataUsageChartObj().data.datasets[1].data.push(0);
    
        configurations.peerDataUsageChartObj().data.datasets[0].lastData = data[data.length - 1].total_sent
        configurations.peerDataUsageChartObj().data.datasets[1].lastData = data[data.length - 1].total_receive
    
    
        for(let i = data.length - 2; i >= 0; i--){
            let sent = data[i].total_sent - configurations.peerDataUsageChartObj().data.datasets[0].lastData;
            let receive = data[i].total_receive - configurations.peerDataUsageChartObj().data.datasets[1].lastData;
            configurations.peerDataUsageChartObj().data.datasets[0].data.push(sent);
            configurations.peerDataUsageChartObj().data.datasets[1].data.push(receive);
            configurations.peerDataUsageChartObj().data.labels.push(data[i].time);
            configurations.peerDataUsageChartObj().data.datasets[0].lastData = data[i].total_sent;
            configurations.peerDataUsageChartObj().data.datasets[1].lastData = data[i].total_receive;
        }
        configurations.peerDataUsageChartObj().update();
    }
}

let peerDataUsageInterval;

$body.on("click", ".btn-data-usage-peer", function(){
    configurations.peerDataUsageChartObj().data.peerID = $(this).data("peer-id");
    configurations.peerDataUsageModal().toggle();
    peerDataUsageInterval = setInterval(function(){
        ajaxPostJSON("/api/getPeerDataUsage", {"config": configurations.getConfigurationName(), "peerID":  configurations.peerDataUsageChartObj().data.peerID, "interval": window.localStorage.getItem("peerTimePeriod")}, loadPeerDataUsageChartDone); 
    }, 30000);
    ajaxPostJSON("/api/getPeerDataUsage", {"config": configurations.getConfigurationName(), "peerID":  configurations.peerDataUsageChartObj().data.peerID, "interval": window.localStorage.getItem("peerTimePeriod")}, loadPeerDataUsageChartDone); 
});

$('#peerDataUsage').on('shown.bs.modal', function() {
    configurations.peerDataUsageChartObj().resize();
}).on('hidden.bs.modal', function() {
    clearInterval(peerDataUsageInterval);
    configurations.peerDataUsageChartObj().data.peerID = "";
    configurations.peerDataUsageChartObj().data.labels = [];
    configurations.peerDataUsageChartObj().data.datasets[0].data = [];
    configurations.peerDataUsageChartObj().data.datasets[1].data = [];
    configurations.peerDataUsageChartObj().update();
});

$(".switchTimePeriod").on("click", function(){
    let peerTimePeriod = window.localStorage.peerTimePeriod;
    $(".switchTimePeriod").removeClass("active");
    $(this).addClass("active");
    if ($(this).data('time') !== peerTimePeriod){
        ajaxPostJSON("/api/getPeerDataUsage", {"config": configurations.getConfigurationName(), "peerID": configurations.peerDataUsageChartObj().data.peerID, "interval": $(this).data('time')}, loadPeerDataUsageChartDone); 
        window.localStorage.peerTimePeriod = $(this).data('time');
    }
    
})


/**
 * Edit Configuration
 */

$editConfiguration = $("#edit_configuration");
$editConfiguration.on("click", function(){
    configurations.getConfigurationDetails();
    configurations.configurationEditModal().toggle();
});


/**
 * ==========
 * Add peers
 * ==========
 */

/**
 * Toggle add peers modal when add button clicked
 */
document.querySelector(".add_btn").addEventListener("click", () => {
    configurations.addModal().toggle();
});

/**
 * When configuration switch got click
 */
$(".toggle--switch").on("change", function(){
    console.log('lol')
    $(this).addClass("waiting").attr("disabled", "disabled");
    let id = configurations.getConfigurationName();
    let status = $(this).prop("checked");
    let ele = $(this);
    $.ajax({
        url: `/switch/${id}`
    }).done(function(res){
        if (res.status){
            if (status){
                configurations.showToast(`${id} is running.`)
            }else{
                configurations.showToast(`${id} is stopped.`)
            }
        }else{
            if (status){
                ele.prop("checked", false)
            }else{
                ele.prop("checked", true)
            }
            configurations.showToast(res.reason);
            $(".index-alert").removeClass("d-none").text(`Configuration toggle failed. Please check the following error message:\n${res.message}`);
        }
        ele.removeClass("waiting");
        ele.removeAttr("disabled");
        configurations.loadPeers($('#search_peer_textbox').val())
    });

});

/**
 * Generate Public key when private got change
 */
document.querySelector("#private_key").addEventListener("change", (event) => {
    let publicKey = document.querySelector("#public_key");
    if (event.target.value.length === 44) {
        publicKey.value = window.wireguard.generatePublicKey(event.target.value);
        publicKey.setAttribute("disabled", "disabled");
    } else {
        publicKey.attributes.removeNamedItem("disabled");
        publicKey.value = "";
    }
});

/**
 * Handle when add modal is show and hide
 */
$('#add_modal').on('show.bs.modal', function() {
    configurations.generateKeyPair();
    configurations.getAvailableIps();
}).on('hide.bs.modal', function() {
    $("#allowed_ips_indicator").html('');
});

/**
 * Handle when user clicked the regenerate button
 */
$("#re_generate_key").on("click", function() {
    $("#public_key").attr("disabled", "disabled");
    $("#re_generate_key i").addClass("rotating");
    configurations.generateKeyPair();
});

/**
 * Handle when user is editing in allowed ips textbox
 */
$("#allowed_ips").on("keyup", function() {
    let s = configurations.cleanIp($(this).val());
    s = s.split(",");
    if (available_ips.includes(s[s.length - 1])) {
        $("#allowed_ips_indicator").removeClass().addClass("text-success")
            .html('<i class="bi bi-check-circle-fill"></i>');
    } else {
        $("#allowed_ips_indicator").removeClass().addClass("text-warning")
            .html('<i class="bi bi-exclamation-circle-fill"></i>');
    }
});

/**
 * Change peer name when user typing in peer name textbox
 */
$("#peer_name_textbox").on("keyup", function() {
    $(".peer_name").html($(this).val());
});

/**
 * When Add Peer button got clicked
 */
$add_peer.addEventListener("click", function() {
    let $bulk_add = $("#bulk_add");
    if ($bulk_add.prop("checked")) {
        if (!$("#new_add_amount").hasClass("is-invalid")) {
            configurations.addPeersByBulk();
        }
    } else {
        let $public_key = $("#public_key");
        let $private_key = $("#private_key");
        let $allowed_ips = $("#allowed_ips");
        $allowed_ips.val(configurations.cleanIp($allowed_ips.val()));
        let $new_add_DNS = $("#new_add_DNS");
        $new_add_DNS.val(configurations.cleanIp($new_add_DNS.val()));
        let $new_add_endpoint_allowed_ip = $("#new_add_endpoint_allowed_ip");
        $new_add_endpoint_allowed_ip.val(configurations.cleanIp($new_add_endpoint_allowed_ip.val()));
        let $new_add_name = $("#new_add_name");
        let $new_add_MTU = $("#new_add_MTU");
        let $new_add_keep_alive = $("#new_add_keep_alive");
        let $enable_preshare_key = $("#enable_preshare_key");
        $add_peer.setAttribute("disabled", "disabled");
        $add_peer.innerHTML = "Adding...";
        if ($allowed_ips.val() !== "" && $public_key.val() !== "" && $new_add_DNS.val() !== "" && $new_add_endpoint_allowed_ip.val() !== "") {
            let conf = configurations.getConfigurationName();
            let data_list = [$private_key, $allowed_ips, $new_add_name, $new_add_DNS, $new_add_endpoint_allowed_ip, $new_add_MTU, $new_add_keep_alive];
            data_list.forEach((ele) => ele.attr("disabled", "disabled"));
            $.ajax({
                method: "POST",
                url: "/add_peer/" + conf,
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({
                    "private_key": $private_key.val(),
                    "public_key": $public_key.val(),
                    "allowed_ips": $allowed_ips.val(),
                    "name": $new_add_name.val(),
                    "DNS": $new_add_DNS.val(),
                    "endpoint_allowed_ip": $new_add_endpoint_allowed_ip.val(),
                    "MTU": $new_add_MTU.val(),
                    "keep_alive": $new_add_keep_alive.val(),
                    "enable_preshared_key": $enable_preshare_key.prop("checked"),
                    "preshared_key": $enable_preshare_key.val()
                }),
                success: function(response) {
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
                        configurations.showToast("Add peer successful!");
                        configurations.addModal().toggle();
                    }
                }
            });
        } else {
            $("#add_peer_alert").html("Please fill in all required box.").removeClass("d-none");
            $add_peer.removeAttribute("disabled");
            $add_peer.innerHTML = "Add";
        }
    }
});

/**
 *  Handle when user is typing the amount of peers they want to add, and will check if the amount is less than 1 or
 *  is larger than the amount of available ips
 */
$("#new_add_amount").on("keyup", function() {
    let $bulk_amount_validation = $("#bulk_amount_validation");
    // $(this).removeClass("is-valid").addClass("is-invalid");
    if ($(this).val().length > 0) {
        if (isNaN($(this).val())) {
            $(this).removeClass("is-valid").addClass("is-invalid");
            $bulk_amount_validation.html("Please enter a valid integer");
        } else if ($(this).val() > available_ips.length) {
            $(this).removeClass("is-valid").addClass("is-invalid");
            $bulk_amount_validation.html(`Cannot create more than ${available_ips.length} peers.`);
        } else if ($(this).val() < 1) {
            $(this).removeClass("is-valid").addClass("is-invalid");
            $bulk_amount_validation.html("Please enter at least 1 or more.");
        } else {
            $(this).removeClass("is-invalid").addClass("is-valid");
        }
    } else {
        $(this).removeClass("is-invalid").removeClass("is-valid");
    }
});

/**
 * Handle when user toggled add peers by bulk
 */
$("#bulk_add").on("change", function() {
    let hide = $(".non-bulk");
    let amount = $("#new_add_amount");
    if ($(this).prop("checked") === true) {
        for (let i = 0; i < hide.length; i++) {
            $(hide[i]).attr("disabled", "disabled");
        }
        amount.removeAttr("disabled");
    } else {
        for (let i = 0; i < hide.length; i++) {
            if ($(hide[i]).attr('id') !== "public_key") {
                $(hide[i]).removeAttr("disabled");
            }
        }
        amount.attr("disabled", "disabled");
    }
});


/**
 * =======================
 * Available IP Related
 * =======================
 */

/**
 * Handle when available ip modal show and hide
 */
$("#available_ip_modal").on("show.bs.modal", () => {
    document.querySelector('#add_modal').classList.add("ip_modal_open");
}).on("hidden.bs.modal", () => {
    document.querySelector('#add_modal').classList.remove("ip_modal_open");
    let ips = [];
    let $selected_ip_list = document.querySelector("#selected_ip_list");
    for (let i = 0; i < $selected_ip_list.childElementCount; i++) {
        ips.push($selected_ip_list.children[i].dataset.ip);
    }
    ips.forEach((ele) => configurations.triggerIp(ele));
});

/**
 * When IP Badge got click
 */
$body.on("click", ".available-ip-badge", function() {
    $(".available-ip-item[data-ip='" + $(this).data("ip") + "']").removeClass("active");
    $(this).remove();
});

/**
 * When available ip item got click
 */
$body.on("click", ".available-ip-item", function() {
    configurations.triggerIp($(this).data("ip"));
});

/**
 * When search IP button got clicked
 */
$("#search_available_ip").on("click", function() {
    configurations.ipModal().toggle();
    let $allowed_ips = document.querySelector("#allowed_ips");
    if ($allowed_ips.value.length > 0) {
        let s = $allowed_ips.value.split(",");
        for (let i = 0; i < s.length; i++) {
            s[i] = s[i].trim();
            configurations.triggerIp(s[i]);
        }
    }
}).tooltip();

/**
 * When confirm IP is clicked
 */
$("#confirm_ip").on("click", () => {
    configurations.ipModal().toggle();
    let ips = [];
    let $selected_ip_list = $("#selected_ip_list");
    $selected_ip_list.children().each(function() {
        ips.push($(this).data("ip"));
    });
    $("#allowed_ips").val(ips.join(", "));
    ips.forEach((ele) => configurations.triggerIp(ele));
});

/**
 * =======
 * QR Code
 * =======
 */

/**
 * When the QR-code button got clicked on each peer
 */
$body.on("click", ".btn-qrcode-peer", function() {
    let src = $(this).data('imgsrc');
    $.ajax({
        "url": src,
        "method": "GET"
    }).done(function(res) {
        $("#qrcode_img").attr('src', res);
        configurations.qrcodeModal().toggle();
    });
});

/**
 * ===========
 * Delete Peer
 * ===========
 */

/**
 * When the delete button got clicked on each peer
 */
$body.on("click", ".btn-delete-peer", function() {
    let peer_id = $(this).data('peer-id')
    $("#delete_peer").data("peer-id", peer_id);
    configurations.deleteModal().toggle();
});

$body.on("click", ".btn-lock-peer", function() {
    configurations.toggleAccess($(this).data('peer-id'), configurations.getConfigurationName());
    if ($(this).hasClass("lock")) {
        console.log($(this).data("peer-name"))
        configurations.showToast(`Enabled ${$(this).children().data("peer-name")}`)
        $(this).removeClass("lock")
        $(this).children().tooltip('hide').attr('data-original-title', 'Peer enabled. Click to disable peer.').tooltip('show');
    } else {
        // Currently unlocked
        configurations.showToast(`Disabled ${$(this).children().data("peer-name")}`)
        $(this).addClass("lock");
        $(this).children().tooltip('hide').attr('data-original-title', 'Peer disabled. Click to enable peer.').tooltip('show');
    }
});

/**
 * When the confirm delete button clicked
 */
$("#delete_peer").on("click", function() {
    $(this).attr("disabled", "disabled");
    $(this).html("Deleting...");
    let config = configurations.getConfigurationName();
    let peer_ids = [$(this).data("peer-id")];
    configurations.deletePeers(config, peer_ids);
});

/**
 * =============
 * Peer Settings
 * =============
 */

/**
 * Handle when setting button got clicked for each peer
 */
$body.on("click", ".btn-setting-peer", function() {
    // configurations.startProgressBar();
    let peer_id = $(this).data("peer-id");
    $("#save_peer_setting").attr("peer_id", peer_id);
    $.ajax({
        method: "POST",
        url: "/get_peer_data/" + configurations.getConfigurationName(),
        headers: {
            "Content-Type": "application/json"
        },
        data: JSON.stringify({ "id": peer_id }),
        success: function(response) {
            let peer_name = ((response.name === "") ? "Untitled" : response.name);
            $("#setting_modal .peer_name").html(peer_name);
            $("#setting_modal #peer_name_textbox").val(response.name);
            $("#setting_modal #peer_private_key_textbox").val(response.private_key);
            $("#setting_modal #peer_DNS_textbox").val(response.DNS);
            $("#setting_modal #peer_allowed_ip_textbox").val(response.allowed_ip);
            $("#setting_modal #peer_endpoint_allowed_ips").val(response.endpoint_allowed_ip);
            $("#setting_modal #peer_mtu").val(response.mtu);
            $("#setting_modal #peer_keep_alive").val(response.keep_alive);
            $("#setting_modal #peer_preshared_key_textbox").val(response.preshared_key);
            configurations.settingModal().toggle();
            configurations.endProgressBar();
        }
    });
});

/**
 * Handle when setting modal is closing
 */
$('#setting_modal').on('hidden.bs.modal', function() {
    $("#setting_peer_alert").addClass("d-none");
});

/**
 * Handle when private key text box in setting modal got changed
 */
$("#peer_private_key_textbox").on("change", function() {
    let $save_peer_setting = $("#save_peer_setting");
    if ($(this).val().length > 0) {
        $.ajax({
            "url": "/check_key_match/" + configurations.getConfigurationName(),
            "method": "POST",
            "headers": { "Content-Type": "application/json" },
            "data": JSON.stringify({
                "private_key": $("#peer_private_key_textbox").val(),
                "public_key": $save_peer_setting.attr("peer_id")
            })
        }).done(function(res) {
            if (res.status === "failed") {
                $("#setting_peer_alert").html(res.status).removeClass("d-none");
            } else {
                $("#setting_peer_alert").addClass("d-none");
            }
        });
    }
});

/**
 * When save peer setting button got clicked
 */
$("#save_peer_setting").on("click", function() {
    $(this).attr("disabled", "disabled");
    $(this).html("Saving...");
    let $peer_DNS_textbox = $("#peer_DNS_textbox");
    let $peer_allowed_ip_textbox = $("#peer_allowed_ip_textbox");
    let $peer_endpoint_allowed_ips = $("#peer_endpoint_allowed_ips");
    let $peer_name_textbox = $("#peer_name_textbox");
    let $peer_private_key_textbox = $("#peer_private_key_textbox");
    let $peer_preshared_key_textbox = $("#peer_preshared_key_textbox");
    let $peer_mtu = $("#peer_mtu");
    let $peer_keep_alive = $("#peer_keep_alive");

    if ($peer_DNS_textbox.val() !== "" &&
        $peer_allowed_ip_textbox.val() !== "" && $peer_endpoint_allowed_ips.val() !== "") {
        let peer_id = $(this).attr("peer_id");
        let conf_id = $(this).attr("conf_id");
        let data_list = [$peer_name_textbox, $peer_DNS_textbox, $peer_private_key_textbox, $peer_preshared_key_textbox, $peer_allowed_ip_textbox, $peer_endpoint_allowed_ips, $peer_mtu, $peer_keep_alive];
        data_list.forEach((ele) => ele.attr("disabled", "disabled"));
        $.ajax({
            method: "POST",
            url: "/save_peer_setting/" + conf_id,
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({
                id: peer_id,
                name: $peer_name_textbox.val(),
                DNS: $peer_DNS_textbox.val(),
                private_key: $peer_private_key_textbox.val(),
                allowed_ip: $peer_allowed_ip_textbox.val(),
                endpoint_allowed_ip: $peer_endpoint_allowed_ips.val(),
                MTU: $peer_mtu.val(),
                keep_alive: $peer_keep_alive.val(),
                preshared_key: $peer_preshared_key_textbox.val()
            }),
            success: function(response) {
                if (response.status === "failed") {
                    $("#setting_peer_alert").html(response.msg).removeClass("d-none");
                } else {
                    configurations.settingModal().toggle();
                    configurations.loadPeers($('#search_peer_textbox').val());
                    $('#alertToast').toast('show');
                    $('#alertToast .toast-body').html("Peer Saved!");
                }
                $("#save_peer_setting").removeAttr("disabled").html("Save");
                data_list.forEach((ele) => ele.removeAttr("disabled"));
            }
        });
    } else {
        $("#setting_peer_alert").html("Please fill in all required box.").removeClass("d-none");
        $("#save_peer_setting").removeAttr("disabled").html("Save");
    }
});

/**
 * Toggle show or hide for the private key textbox in the setting modal
 */
$(".peer_private_key_textbox_switch").on("click", function() {
    let $peer_private_key_textbox = $("#peer_private_key_textbox");
    let mode = (($peer_private_key_textbox.attr('type') === 'password') ? "text" : "password");
    let icon = (($peer_private_key_textbox.attr('type') === 'password') ? "bi bi-eye-slash-fill" : "bi bi-eye-fill");
    $peer_private_key_textbox.attr('type', mode);
    $(".peer_private_key_textbox_switch i").removeClass().addClass(icon);
});

/**
 * ===========
 * Search Peer
 * ===========
 */

let typingTimer; // Timeout object
let doneTypingInterval = 200; // Timeout interval

/**
 * Handle when the user keyup and keydown on the search textbox
 */
$('#search_peer_textbox').on('keyup', function() {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        configurations.loadPeers($(this).val());
    }, doneTypingInterval);
}).on('keydown', function() {
    clearTimeout(typingTimer);
});

/**
 * Manage Peers
 */

/**
 * Handle when sort peers changed
 */
$body.on("change", "#sort_by_dropdown", function() {
    $.ajax({
        method: "POST",
        data: JSON.stringify({ 'sort': $("#sort_by_dropdown option:selected").val() }),
        headers: { "Content-Type": "application/json" },
        url: "/update_dashboard_sort",
        success: function() {
            configurations.loadPeers($('#search_peer_textbox').val());
        }
    });
});

/**
 * Handle copy public key
 */
$body.on("mouseenter", ".key", function() {
    let label = $(this).parent().siblings().children()[1];
    label.style.opacity = "100";
}).on("mouseout", ".key", function() {
    let label = $(this).parent().siblings().children()[1];
    label.style.opacity = "0";
    setTimeout(function() {
        label.innerHTML = "CLICK TO COPY";
    }, 200);
}).on("click", ".key", function() {
    let label = $(this).parent().siblings().children()[1];
    configurations.copyToClipboard($(this));
    label.innerHTML = "COPIED!";
});

/**
 * Handle when interval button got clicked
 */
$body.on("click", ".update_interval", function() {
    $(".interval-btn-group button").removeClass("active");
    let _new = $(this);
    _new.addClass("active");
    let interval = $(this).data("refresh-interval");
    if ([5000, 10000, 30000, 60000].includes(interval)) {
        configurations.updateRefreshInterval(interval);
    }



    // $.ajax({
    //     method:"POST",
    //     data: "interval="+$(this).data("refresh-interval"),
    //     url: "/update_dashboard_refresh_interval",
    //     success: function (res){
    //         configurations.updateRefreshInterval(res, interval);
    //     }
    // });
});

/**
 * Handle when refresh button got clicked
 */
$body.on("click", ".refresh", function() {
    configurations.loadPeers($('#search_peer_textbox').val());
});

/**
 * Handle when display mode button got clicked
 */
$body.on("click", ".display_mode", function() {
    $(".display-btn-group button").removeClass("active");
    $(this).addClass("active");
    window.localStorage.setItem("displayMode", $(this).data("display-mode"));
    configurations.updateDisplayMode();
    if ($(this).data("display-mode") === "list") {
        Array($(".peer_list").children()).forEach(function(child) {
            $(child).removeClass().addClass("col-12");
        });
        configurations.showToast("Displaying as List");
    } else {
        Array($(".peer_list").children()).forEach(function(child) {
            $(child).removeClass().addClass("col-sm-6 col-lg-4");
        });
        configurations.showToast("Displaying as Grids");
    }
});


/**
 * =================
 * Configuration Menu
 * =================
 */
let $setting_btn_menu = $(".setting_btn_menu");
$setting_btn_menu.css("top", ($setting_btn_menu.height() + 54) * (-1));
let $setting_btn = $(".setting_btn");

/**
 * When the menu button got clicked
 */
$setting_btn.on("click", function() {
    if ($setting_btn_menu.hasClass("show")) {
        $setting_btn_menu.removeClass("showing");
        setTimeout(function() {
            $setting_btn_menu.removeClass("show");
        }, 201);
    } else {
        $setting_btn_menu.addClass("show");
        setTimeout(function() {
            $setting_btn_menu.addClass("showing");
        }, 10);
    }
});

/**
 * Whenever the user clicked, if it is outside the menu and the menu is opened, hide the menu
 */
$("html").on("click", function(r) {
    if (document.querySelector(".setting_btn") !== r.target) {
        if (!document.querySelector(".setting_btn").contains(r.target)) {
            if (!document.querySelector(".setting_btn_menu").contains(r.target)) {
                $setting_btn_menu.removeClass("showing");
                setTimeout(function() {
                    $setting_btn_menu.removeClass("show");
                }, 310);
            }
        }
    }
});


/**
 * ====================
 * Delete Peers by Bulk
 * ====================
 */

/**
 * When delete peers by bulk clicked
 */
$("#delete_peers_by_bulk_btn").on("click", () => {
    let $delete_bulk_modal_list = $("#delete_bulk_modal .list-group");
    $delete_bulk_modal_list.html('');
    peers.forEach((peer) => {
        let name;
        if (peer.name === "") { name = "Untitled Peer"; } else { name = peer.name; }
        $delete_bulk_modal_list.append('<a class="list-group-item list-group-item-action delete-bulk-peer-item" style="cursor: pointer" data-id="' +
            peer.id + '" data-name="' + name + '">' + name + '<br><code>' + peer.id + '</code></a>');
    });
    configurations.deleteBulkModal().toggle();
});

/**
 * When the item or tag of delete peers by bulk got clicked
 */
$body.on("click", ".delete-bulk-peer-item", function() {
    configurations.toggleDeleteByBulkIP($(this));
}).on("click", ".delete-peer-bulk-badge", function() {
    configurations.toggleDeleteByBulkIP($(".delete-bulk-peer-item[data-id='" + $(this).data("id") + "']"));
});

let $selected_peer_list = document.getElementById("selected_peer_list");

/**
 * The change observer to observe when user choose 1 or more peers to delete
 * @type {MutationObserver}
 */
let changeObserver = new MutationObserver(function() {
    if ($selected_peer_list.hasChildNodes()) {
        $("#confirm_delete_bulk_peers").removeAttr("disabled");
    } else {
        $("#confirm_delete_bulk_peers").attr("disabled", "disabled");
    }
});
changeObserver.observe($selected_peer_list, {
    attributes: true,
    childList: true,
    characterData: true
});

let confirm_delete_bulk_peers_interval;

/**
 * When the user clicked the delete button in the delete peers by bulk
 */
$("#confirm_delete_bulk_peers").on("click", function() {
    let btn = $(this);
    if (confirm_delete_bulk_peers_interval !== undefined) {
        clearInterval(confirm_delete_bulk_peers_interval);
        confirm_delete_bulk_peers_interval = undefined;
        btn.html("Delete");
    } else {
        let timer = 5;
        btn.html(`Deleting in ${timer} secs... Click to cancel`);
        confirm_delete_bulk_peers_interval = setInterval(function() {
            timer -= 1;
            btn.html(`Deleting in ${timer} secs... Click to cancel`);
            if (timer === 0) {
                btn.html(`Deleting...`);
                btn.attr("disabled", "disabled");
                let ips = [];
                $selected_peer_list.childNodes.forEach((ele) => ips.push(ele.dataset.id));
                configurations.deletePeers(configurations.getConfigurationName(), ips);
                clearInterval(confirm_delete_bulk_peers_interval);
                confirm_delete_bulk_peers_interval = undefined;
            }
        }, 1000);
    }
});

/**
 * Select all peers to delete
 */
$("#select_all_delete_bulk_peers").on("click", function() {
    $(".delete-bulk-peer-item").each(function() {
        if (!$(this).hasClass("active")) {
            configurations.toggleDeleteByBulkIP($(this));
        }
    });
});

/**
 * When delete peers by bulk window is hidden
 */
$(configurations.deleteBulkModal()._element).on("hidden.bs.modal", function() {
    $(".delete-bulk-peer-item").each(function() {
        if ($(this).hasClass("active")) {
            configurations.toggleDeleteByBulkIP($(this));
        }
    });
});

/**
 * ==============
 * Download Peers
 * ==============
 */

/**
 * When the download peers button got clicked
 */
$body.on("click", ".btn-download-peer", function(e) {
    e.preventDefault();
    let link = $(this).attr("href");
    $.ajax({
        "url": link,
        "method": "GET",
        success: function(res) {
            configurations.downloadOneConfig(res);
        }
    });
});

/**
 * When the download all peers got clicked
 */
$("#download_all_peers").on("click", function() {
    $.ajax({
        "url": `/download_all/${configurations.getConfigurationName()}`,
        "method": "GET",
        success: function(res) {
            if (res.peers.length > 0) {
                window.wireguard.generateZipFiles(res);
                configurations.showToast("Peers' zip file download successful!");
            } else {
                configurations.showToast("Oops! There are no peer can be download.");
            }
        }
    });
});