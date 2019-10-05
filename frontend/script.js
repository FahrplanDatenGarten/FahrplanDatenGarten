$(document).ready(function(){
    var url = "https://raw.githubusercontent.com/Jugendhackt/FahrplanDatenGarten/master/demo.json";
    $.ajax({
        url: url,
        dataType: 'json'
    })
    .done(function(data){
        console.log(data);
        var delayed = data.journeys_delayed;
        var mostNumber = data.biggest_delay[0].name;
        var mostMinutes = data.biggest_delay[0].delay;
        var average = data.average_delay;
        //console.log(bio);
        $("#train-count").text(delayed);
        $("#most-number").text(mostNumber);
        $("#most-minutes").text(mostMinutes);
        $("#average").text(average);
    });
    
});
