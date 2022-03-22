let numberToast = 0;
let addConfigurationModal = new bootstrap.Modal(document.getElementById('addConfigurationModal'), {
    keyboard: false,
    backdrop: 'static'
});

function showToast(msg){
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

$(".toggle--switch").on("change", function(){
    $(this).addClass("waiting").attr("disabled", "disabled");
    let id = $(this).data("conf-id");
    let status = $(this).prop("checked");
    let ele = $(this);
    let label = $(this).siblings("label");
    $.ajax({
        url: `/switch/${id}`
    }).done(function(res){
        let dot = $(`div[data-conf-id="${id}"] .dot`);
        console.log();
        if (res){
            if (status){
                dot.removeClass("dot-stopped").addClass("dot-running");
                dot.siblings().text("Running");
                showToast(`${id} is running.`)
            }else{
                dot.removeClass("dot-running").addClass("dot-stopped");
                showToast(`${id} is stopped.`)
            }
            ele.removeClass("waiting");
            ele.removeAttr("disabled");
        }else{
            if (status){
                $(this).prop("checked", false)
            }else{
                $(this).prop("checked", true)
            }
        }
        
    })
});

$('.switch').on("click", function() {
    $(this).siblings($(".spinner-border")).css("display", "inline-block")
    $(this).remove()
    location.replace("/switch/"+$(this).attr('id'))
});
$(".sb-home-url").addClass("active");

$(".card-body").on("click", function(handle){
    if ($(handle.target).attr("class") !== "toggleLabel" && $(handle.target).attr("class") !== "toggle--switch") {
        window.open($(this).find("a").attr("href"), "_self");
    }
});

function genKeyPair(){
    let keyPair = window.wireguard.generateKeypair(); 
    $("#addConfigurationPrivateKey").val(keyPair.privateKey);
    $("#addConfigurationPublicKey").attr("disabled", "disabled").val(keyPair.publicKey);
}

$("#reGeneratePrivateKey").on("click", function() {
    genKeyPair();
});

$("#toggleAddConfiguration").on("click", function(){
    addConfigurationModal.toggle();
    genKeyPair()
}); 

$("#addConfigurationPrivateKey").on("change", function() {
    let $publicKey = $("#addConfigurationPublicKey");
    if ($(this).val().length === 44) {
        $publicKey.attr("disabled", "disabled").val(window.wireguard.generatePublicKey($(this).val()));
    } else {
        $publicKey.removeAttr("disabled").val("");
    }
});

$("#addConfigurationAddress").on("change", function(){
    let address = $("#addConfigurationAddress");
    let addressFeedback = $("#addConfigurationAddressFeedback");
    let availableIPs = $(".addConfigurationAvailableIPs");
    $.ajax({
        url: "/api/addConfigurationAddressCheck",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        data: JSON.stringify({
            "address": $(this).val()
        })
    }).done(function(res){
        console.log(res)
        if (res.status){
            availableIPs.html(`<strong>${res.data}</strong>`);
            address.removeClass("is-invalid").addClass("is-valid");
        }else{
            address.addClass("is-invalid");
            addressFeedback.addClass("invalid-feedback").text(res.reason);
            availableIPs.html(`N/A`);
        }
    })
});