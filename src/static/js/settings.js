$(".sb-settings-url").addClass("active")
$(".confirm_modal").click(function () {
    $(".app_new_ip").html($("#app_ip")[0].value)
    $(".app_new_port").html($("#app_port")[0].value)
})

$(".confirm_restart").click(function () {
    $(".cancel_restart").remove()
    countdown = 7;
    $.post('/update_app_ip_port', $('.update_app_ip_port').serialize())
    url = $("#app_ip")[0].value + ":" + $("#app_port")[0].value;
    $(".confirm_restart").attr("disabled", "disabled")
    setInterval(function () {
        if (countdown === 0) {
            window.location.replace("http://" + url);
        }
        $(".confirm_restart").html("Redirecting you in " + countdown + " seconds.")
        countdown--;
    }, 1000)
});

$(".change_path").click(function () {
    $(this).attr("disabled", "disabled");
    countdown = 5;
    setInterval(function () {
        if (countdown === 0) {
            location.reload()
        }
        $(".change_path").html("Redirecting you in " + countdown + " seconds.")
        countdown--;
    }, 1000)
    $.post('/update_wg_conf_path', $('.update_wg_conf_path').serialize())
});

$(".bottomNavSettings").addClass("active");


$(".theme-switch-btn").on("click", function(){
    if (!$(this).hasClass("active")){
        let theme = $(this).data("theme");
        $(".theme-switch-btn").removeClass("active");
        $(this).addClass("active");
        $.ajax({
            method: "POST",
            url: "/api/settings/setTheme",
            headers: {"Content-Type": "application/json"},
            data: JSON.stringify({"theme": theme})
        }).done(function(res){
            if (res.status == true){
                if (theme == "light"){
                    $("#darkThemeCSS").remove();
                    showToast("Switched to light theme");
                }else{
                    $("head").append('<link rel="stylesheet" type="text/css" href="/static/css/theme/dark.min.css" id="darkThemeCSS">');
                    showToast("Switched to dark theme");
                }
            }
        });
    }
});