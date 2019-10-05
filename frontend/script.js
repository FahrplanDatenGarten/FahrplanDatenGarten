$(document).ready(function () {
    load();
});
function load() {
    $("#body").hide();
    $("#loading").show();
    $.ajax({
        url: $("#content").attr("view"),
        dataType: 'html'
    }).done(function (data) {
        $("#content").html(data);
        var url = "https://raw.githubusercontent.com/Jugendhackt/FahrplanDatenGarten/master/demo.json";
        $.ajax({
            url: url,
            dataType: 'json'
        })
            .done(function (data) {
                console.log(data);
                var averagejourneys = data.average_journeys;
                var mostNumber = data.biggest_delay[0].name;
                var mostMinutes = data.biggest_delay[0].delay;
                var currentaverage = data.average_delay;
                //console.log(bio);
                
			    $("#train-count").text(averagejourneys + "%");
                $("#most-number").text(mostNumber);
                $("#most-minutes").text(mostMinutes);
                $("#average").text(currentaverage);

                $("#loading").fadeOut(function () {
                    $("#body").fadeIn();


                    $(".ajax-link").each(function () {
                        $(this).click(function (event) {
                            $("#content").attr("view", $(this).attr("href"));
                            load();
                            event.preventDefault();
                            return false;
                        });
                    });
                });
            });
    });

}