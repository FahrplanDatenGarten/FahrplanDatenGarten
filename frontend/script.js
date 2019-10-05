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
                var averagejourneys = data.journeys_delayed / data.current_journeys;
                averagejourneys = (averagejourneys*100).toFixed(2);
                


                var ctx = document.getElementById('train-chart').getContext('2d');
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                        datasets: [{
                            label: '# of Votes',
                            data: [12, 19, 3, 5, 2, 3],
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.2)',
                                'rgba(54, 162, 235, 0.2)'
                            ],
                            borderColor: [
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                }
                            }]
                        }
                    }
                });
                
			    $("#train-chart").text(averagejourneys + "%");
                $("#most-number").text(mostNumber);
                $("#most-minutes").text(mostMinutes);
                $("#average").text(currentaverage);



                console.log("123");
                var zugformular = $("#zugformular");
                if (zugformular.length){
                    console.log("test");
                    zugformular.closest('form').on('submit', function(e){
                
                        console.log("Hello");
                        e.preventDefault();
                        
                    });
                }
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