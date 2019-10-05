$(document).ready(function(){
    $("#body").hide();
    $("#loading").show();
    var url = "https://raw.githubusercontent.com/Jugendhackt/FahrplanDatenGarten/master/demo.json";
    $.ajax({
        url: url,
        dataType: 'json'
    })
    .done(function(data){
        console.log(data);
        var currentdelayed = data.journeys_delayed;
        var mostNumber = data.biggest_delay[0].name;
        var mostMinutes = data.biggest_delay[0].delay;
        var currentaverage = data.average_delay;
        //console.log(bio);
        $("#train-count").text(currentdelayed);
        $("#most-number").text(mostNumber);
        $("#most-minutes").text(mostMinutes);
        $("#average").text(currentaverage);

        $("#loading").fadeOut(function(){
            $("#body").fadeIn();
        });
    });
    
});
