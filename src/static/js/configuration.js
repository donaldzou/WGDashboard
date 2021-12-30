let $body = $("body");

// Progress Bar
let $progress_bar = $(".progress-bar");
function startProgressBar(){
    $progress_bar.css("width","0%")
        .css("opacity", "100")
        .css("background", "rgb(255,69,69)")
        .css("background",
            "linear-gradient(145deg, rgba(255,69,69,1) 0%, rgba(0,115,186,1) 100%)")
        .css("width","25%");
    setTimeout(function(){
        stillLoadingProgressBar();
    },300);
}
function stillLoadingProgressBar(){
    $progress_bar.css("transition", "3s ease-in-out").css("width", "75%");
}
function endProgressBar(){
    $progress_bar.css("transition", "0.3s ease-in-out").css("width","100%");
    setTimeout(function(){
        $progress_bar.css("opacity", "0");
    },250);

}

function showToast(msg) {
    $('#alertToast').toast('show');
    $('#alertToast .toast-body').html(msg);
}


// Config Toggle
$body.on("click", ".switch", function (){
    $(this).siblings($(".spinner-border")).css("display", "inline-block");
     $(this).remove();
   location.replace("/switch/"+$(this).attr('id'));
});

// Generating Keys
function generate_key(){
    $.ajax({
        "url": "/generate_peer",
        "method": "GET",
    }).done(function(res){
        $("#private_key").val(res.private_key);
        $("#public_key").val(res.public_key);
        $("#preshare_key").val(res.preshared_key);
        $("#add_peer_alert").addClass("d-none");
        $("#re_generate_key i").removeClass("rotating");
    });
}
function generate_public_key(){
    $.ajax({
        "url": "/generate_public_key",
        "method": "POST",
        "headers":{"Content-Type": "application/json"},
        "data": JSON.stringify({"private_key": $("#private_key").val()})
    }).done(function(res){
        if(res.status === "failed"){
            $("#add_peer_alert").html(res.msg).removeClass("d-none");
        }else{
            $("#add_peer_alert").addClass("d-none");
        }
        $("#public_key").val(res.data);
         $("#re_generate_key i").removeClass("rotating");
    });
}

// Add Peer
$("#private_key").on("change",function(){
    if ($(this).val().length > 0){
        $("#re_generate_key i").addClass("rotating");
        generate_public_key();
    }else{
        $("#public_key").removeAttr("disabled").val("");
    }
});

$('#add_modal').on('show.bs.modal', function (event) {
    generate_key();
});
$("#re_generate_key").on("click",function (){
    $("#public_key").attr("disabled","disabled");
    $("#re_generate_key i").addClass("rotating");
    generate_key();
});
let addModal = new bootstrap.Modal(document.getElementById('add_modal'), {
    keyboard: false
});

$(".add_btn").on("click", function(){
    addModal.toggle();
});

$("#save_peer").on("click",function(){
    let $public_key = $("#public_key");
    let $private_key = $("#private_key");
    let $allowed_ips = $("#allowed_ips");
    let $new_add_DNS = $("#new_add_DNS");
    let $new_add_endpoint_allowed_ip = $("#new_add_endpoint_allowed_ip");
    let $new_add_name = $("#new_add_name");
    let $new_add_MTU = $("#new_add_MTU");
    let $new_add_keep_alive = $("#new_add_keep_alive");
    let $enable_preshare_key = $("#enable_preshare_key");

    $(this).attr("disabled","disabled");
    $(this).html("Saving...");
    if ($allowed_ips.val() !== "" && $public_key.val() !== "" && $new_add_DNS.val() !== "" && $new_add_endpoint_allowed_ip.val() !== ""){
        let conf = $(this).attr('conf_id');
        let data_list = [$private_key, $allowed_ips, $new_add_name, $new_add_DNS, $new_add_endpoint_allowed_ip,$new_add_MTU, $new_add_keep_alive];
        data_list.forEach((ele) => ele.attr("disabled", "disabled"));
        $.ajax({
            method: "POST",
            url: "/add_peer/"+conf,
            headers:{
                "Content-Type": "application/json"
            },
            data: JSON.stringify({
                "private_key":$private_key.val(),
                "public_key":$public_key.val(),
                "allowed_ips": $allowed_ips.val(),
                "name":$new_add_name.val(),
                "DNS": $new_add_DNS.val(),
                "endpoint_allowed_ip": $new_add_endpoint_allowed_ip.val(),
                "MTU": $new_add_MTU.val(),
                "keep_alive": $new_add_keep_alive.val(),
                "enable_preshared_key": $enable_preshare_key.prop("checked"),
            }),
            success: function (response){
                if(response !== "true"){
                    $("#add_peer_alert").html(response).removeClass("d-none");
                    data_list.forEach((ele) => ele.removeAttr("disabled"));
                    $("#save_peer").removeAttr("disabled").html("Save");
                }
                else{
                    load_data("");
                    addModal.toggle();
                }
            }
        });
    }else{
        $("#add_peer_alert").html("Please fill in all required box.").removeClass("d-none");
        $(this).removeAttr("disabled");
        $(this).html("Save");
    }
});


let qrcodeModal = new bootstrap.Modal(document.getElementById('qrcode_modal'), {
    keyboard: false
});
// QR Code
$body.on("click", ".btn-qrcode-peer", function (){
    let src = $(this).attr('img_src');
    $.ajax({
        "url": src,
        "method": "GET"
    }).done(function(res){
        $("#qrcode_img").attr('src', res);
        qrcodeModal.toggle();
    });
});

// Delete Peer Modal
let deleteModal = new bootstrap.Modal(document.getElementById('delete_modal'), {
    keyboard: false
});

$body.on("click", ".btn-delete-peer", function(){
    let peer_id = $(this).attr("id");
    $("#delete_peer").attr("peer_id", peer_id);
    deleteModal.toggle();
});

$("#delete_peer").on("click",function(){
    $(this).attr("disabled","disabled");
    $(this).html("Deleting...");
    let peer_id = $(this).attr("peer_id");
    let config = $(this).attr("conf_id");
    $.ajax({
        method: "POST",
        url: "/remove_peer/"+config,
        headers:{
            "Content-Type": "application/json"
        },
        data: JSON.stringify({"action": "delete", "peer_id": peer_id}),
        success: function (response){
            if(response !== "true"){
                $("#remove_peer_alert").html(response+$("#add_peer_alert").html()).removeClass("d-none");
            }
            else{
                deleteModal.toggle();
                load_data($('#search_peer_textbox').val());
                $('#alertToast').toast('show');
                $('#alertToast .toast-body').html("Peer deleted!");
                $("#delete_peer").removeAttr("disabled").html("Delete");
            }
        }
    });
});

// Peer Setting Modal
let settingModal = new bootstrap.Modal(document.getElementById('setting_modal'), {
    keyboard: false
});
$body.on("click", ".btn-setting-peer", function(){
    startProgressBar();
    let peer_id = $(this).attr("id");
    $("#save_peer_setting").attr("peer_id", peer_id);
    $.ajax({
        method: "POST",
        url: "/get_peer_data/"+$("#setting_modal").attr("conf_id"),
        headers:{
            "Content-Type": "application/json"
        },
        data: JSON.stringify({"id": peer_id}),
        success: function(response){
            let peer_name = ((response.name === "") ? "Untitled Peer" : response.name);
            $("#setting_modal .peer_name").html(peer_name);
            $("#setting_modal #peer_name_textbox").val(response.name);
            $("#setting_modal #peer_private_key_textbox").val(response.private_key);
            $("#setting_modal #peer_DNS_textbox").val(response.DNS);
            $("#setting_modal #peer_allowed_ip_textbox").val(response.allowed_ip);
            $("#setting_modal #peer_endpoint_allowed_ips").val(response.endpoint_allowed_ip);
            $("#setting_modal #peer_mtu").val(response.mtu);
            $("#setting_modal #peer_keep_alive").val(response.keep_alive);
            $("#setting_modal #peer_preshared_key_textbox").val(response.preshared_key);
            settingModal.toggle();
            endProgressBar();
        }
    });
});

$('#setting_modal').on('hidden.bs.modal', function (event) {
  $("#setting_peer_alert").addClass("d-none");
});

$("#peer_private_key_textbox").on("change",function(){
    let $save_peer_setting = $("#save_peer_setting");
    if ($(this).val().length > 0){
        $.ajax({
            "url": "/check_key_match/"+$save_peer_setting.attr("conf_id"),
            "method": "POST",
            "headers":{"Content-Type": "application/json"},
            "data": JSON.stringify({
                "private_key": $("#peer_private_key_textbox").val(),
                "public_key": $save_peer_setting.attr("peer_id")
            })
        }).done(function(res){
            if(res.status === "failed"){
                $("#setting_peer_alert").html(res.status).removeClass("d-none");
            }else{
                $("#setting_peer_alert").addClass("d-none");
            }
        });
    }
});

$("#save_peer_setting").on("click",function (){
    $(this).attr("disabled","disabled");
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
        $peer_allowed_ip_textbox.val() !== "" && $peer_endpoint_allowed_ips.val() !== ""){
        let peer_id = $(this).attr("peer_id");
        let conf_id = $(this).attr("conf_id");
        let data_list = [$peer_name_textbox, $peer_DNS_textbox, $peer_private_key_textbox, $peer_preshared_key_textbox, $peer_allowed_ip_textbox, $peer_endpoint_allowed_ips, $peer_mtu, $peer_keep_alive];
        data_list.forEach((ele) => ele.attr("disabled","disabled"));
        $.ajax({
            method: "POST",
            url: "/save_peer_setting/"+conf_id,
            headers:{
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
            success: function (response){
                if (response.status === "failed"){
                    $("#setting_peer_alert").html(response.msg).removeClass("d-none");
                }else{
                    settingModal.toggle();
                    load_data($('#search_peer_textbox').val());
                    $('#alertToast').toast('show');
                    $('#alertToast .toast-body').html("Peer Saved!");
                }
                $("#save_peer_setting").removeAttr("disabled").html("Save");
                data_list.forEach((ele) => ele.removeAttr("disabled"));
            }
        });
        }else{
        $("#setting_peer_alert").html("Please fill in all required box.").removeClass("d-none");
        $("#save_peer_setting").removeAttr("disabled").html("Save");
    }
});

$(".peer_private_key_textbox_switch").on("click",function (){
    let $peer_private_key_textbox = $("#peer_private_key_textbox");
    let mode = (($peer_private_key_textbox.attr('type') === 'password') ? "text":"password");
    let icon = (($peer_private_key_textbox.attr('type') === 'password') ? "bi bi-eye-slash-fill":"bi bi-eye-fill");
    $peer_private_key_textbox.attr('type',mode);
    $(".peer_private_key_textbox_switch i").removeClass().addClass(icon);
});


// Search Peer
let typingTimer;
let doneTypingInterval = 200;
let $input = $('#search_peer_textbox');
$input.on('keyup', function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(doneTyping, doneTypingInterval);
});
$input.on('keydown', function () {
    clearTimeout(typingTimer);
});
function doneTyping () {
    load_data($input.val());
}


// Sorting
$body.on("change", "#sort_by_dropdown", function (){
    $.ajax({
        method:"POST",
        data: JSON.stringify({'sort':$("#sort_by_dropdown option:selected").val()}),
        headers:{"Content-Type": "application/json"},
        url: "/update_dashboard_sort",
        success: function (res){
            load_data($('#search_peer_textbox').val());
        }
    });
});

// Click key to copy animation
$body.on("mouseenter", ".key", function(){
    let label = $(this).parent().siblings().children()[1];
    label.style.opacity = "100";
})
$body.on("mouseout", ".key", function(){
    let label = $(this).parent().siblings().children()[1];
    label.style.opacity = "0";
    setTimeout(function (){
        label.innerHTML = "CLICK TO COPY";
    },200);
});

$body.on("click", ".key", function(){
    var label = $(this).parent().siblings().children()[1];
    copyToClipboard($(this));
    label.innerHTML = "COPIED!";
});

/**
 * CopyToClipboard
 * @param element
 */
function copyToClipboard(element) {
    let $temp = $("<input>");
    $body.append($temp);
    $temp.val($(element).text()).trigger( "select" );
    document.execCommand("copy");
    $temp.remove();
}

// Update Interval
$body.on("click", ".update_interval", function(){
    let prev = $(".interval-btn-group.active button");
    $(".interval-btn-group button").removeClass("active");
    let _new = $(this);
    _new.addClass("active");
    let interval = $(this).data("refresh-interval");
    $.ajax({
        method:"POST",
        data: "interval="+$(this).data("refresh-interval"),
        url: "/update_dashboard_refresh_interval",
        success: function (res){
            if (res === "true"){
                load_interval = interval;
                clearInterval(load_timeout);
                load_timeout = setInterval(function (){
                    load_data($('#search_peer_textbox').val());
                }, interval);
                showToast("Refresh Interval set to "+Math.round(interval/1000)+" seconds");
            }else{
                $(".interval-btn-group button").removeClass("active");
                $('.interval-btn-group button[data-refresh-interval="'+load_interval+'"]').addClass("active");
                showToast("Refresh Interval set unsuccessful");
            }
        }
    })
});

// Refresh Button
$body.on("click", ".refresh", function (){
    load_data($('#search_peer_textbox').val());
});


// Switch display mode
$body.on("click", ".display_mode", function(){
    $(".display-btn-group button").removeClass("active");
    $(this).addClass("active");
    let display_mode = $(this).data("display-mode");
    $.ajax({
        method:"GET",
        url: "/switch_display_mode/"+$(this).data("display-mode"),
        success: function (res){
           if (res === "true"){
                if (display_mode === "list"){
                Array($(".peer_list").children()).forEach(function(child){
                    $(child).removeClass().addClass("col-12");
                });
                showToast("Displaying as List");
            }else{
               Array($(".peer_list").children()).forEach(function(child){
                    $(child).removeClass().addClass("col-sm-6 col-lg-4");
               });
               showToast("Displaying as Grid");
            }
           }
        }
    });
});