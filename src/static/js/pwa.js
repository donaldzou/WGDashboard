let wrapper = $(".bottomNavWrapper");
$(".bottomNavConfigs").on("click", function(){
    let subNav = $(this).children(".subNav");
    subNav.removeClass("animate__fadeOutDown").addClass("active animate__fadeInUp");
    wrapper.fadeIn();
});

$(".bottomNavHome").on("click", function(){
    window.location.replace('/')
});

$(".bottomNavSettings").on("click", function(){
    window.location.replace('/settings')
})


function hideBottomSubNav(){
    $(".bottomNavButton .subNav").removeClass("animate__fadeInUp").addClass("animate__fadeOutDown");
    wrapper.fadeOut();
    setTimeout(function(){
        $(".bottomNavButton .subNav").removeClass("active");
    },350)
}

wrapper.on("click", function(){
    hideBottomSubNav();
});


$(".bottomNavMore").on("click", function(){
    let subNav = $(this).children(".subNav");
    subNav.removeClass("animate__fadeOutDown").addClass("active animate__fadeInUp");
    wrapper.fadeIn();
});

// $(".bottomNavButton .nav-conf-link").on("click", function(){
//     hideBottomSubNav();
// })