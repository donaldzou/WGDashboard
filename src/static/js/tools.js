$(".ip_dropdown").change(function (){
    $(".modal.show .btn").removeAttr("disabled")
});
$(".conf_dropdown").change(function (){
    $(".modal.show .ip_dropdown").html('<option value="none" selected="selected" disabled>Loading...')
    $.ajax({
        url: "/get_ping_ip",
        method: "POST",
        data: "config="+$(this).children("option:selected").val(),
        success: function (res){
            $(".modal.show .ip_dropdown").html("")
            $(".modal.show .ip_dropdown").append('<option value="none" selected="selected" disabled>Choose an IP')
            $(".modal.show .ip_dropdown").append(res)
        }
    })
});


// Ping Tools



$(".send_ping").click(function (){
    $(this).attr("disabled","disabled")
    $(this).html("Pinging...")
    $("#ping_modal .form-control").attr("disabled","disabled")
    $.ajax({
        method:"POST",
        data: "ip="+$(':selected', $("#ping_modal .ip_dropdown")).val()+"&count="+$("#ping_modal .ping_count").val(),
        url: "/ping_ip",
        success: function (res){
            $(".ping_result tbody").html("")
            html = '<tr><th scope="row">Address</th><td>'+res['address']+'</td></tr>' +
                '<tr><th scope="row">Is Alive</th><td>'+res['is_alive']+'</td></tr>' +
                '<tr><th scope="row">Min RTT</th><td>'+res['min_rtt']+'ms</td></tr>' +
                '<tr><th scope="row">Average RTT </th><td>'+res['avg_rtt']+'ms</td></tr>' +
                '<tr><th scope="row">Max RTT</th><td>'+res['max_rtt']+'ms</td></tr>' +
                '<tr><th scope="row">Package Sent</th><td>'+res['package_sent']+'</td></tr>' +
                '<tr><th scope="row">Package Received</th><td>'+res['package_received']+'</td></tr>' +
                '<tr><th scope="row">Package Loss</th><td>'+res['package_loss']+'</td></tr>'
            $(".ping_result tbody").html(html)
            $(".send_ping").removeAttr("disabled")
            $(".send_ping").html("Ping")
            $("#ping_modal .form-control").removeAttr("disabled")
        }
    })
});

// Traceroute Tools
$(".send_traceroute").click(function (){
    $(this).attr("disabled","disabled")
    $(this).html("Tracing...");
    $("#traceroute_modal .form-control").attr("disabled","disabled")
    $.ajax({
        url: "/traceroute_ip",
        method: "POST",
        data: "ip="+$(':selected', $("#traceroute_modal .ip_dropdown")).val(),
        success: function (res){
            $(".traceroute_result tbody").html("");
            for (i in res){
               $(".traceroute_result tbody").append('<tr><th scope="row">'+res[i]['hop']+'</th><td>'+res[i]['ip']+'</td><td>'+res[i]['avg_rtt']+'</td><td>'+res[i]['min_rtt']+'</td><td>'+res[i]['max_rtt']+'</td></tr>')
            }
            $(".send_traceroute").removeAttr("disabled");
            $(".send_traceroute").html("Traceroute");
            $("#traceroute_modal .form-control").removeAttr("disabled")
        }
    })
})