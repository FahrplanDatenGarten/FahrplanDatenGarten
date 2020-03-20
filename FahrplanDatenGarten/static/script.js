$(document).ready(function() {
    load();
});

function load() {
    $("#body").hide();
    $("#loading").show();
    $.ajax({
        url: $("#content").attr("view"),
        dataType: 'html'
    }).done(function(data) {
        $("#content").html(data);
        standartdaten();
        pageload();
    });
}

function pageload() {
    $("#loading").fadeOut(function() {
        $("#body").fadeIn();


        $(".ajax-link").each(function() {
            $(this).click(function(event) {
                $("#content").attr("view", $(this).attr("href"));
                load();
                event.preventDefault();
                return false;
            });
        });
    });

}

function standartdaten() {
    if (!$("#train-percentage-chart").length)
        return;
    var url = "/verspaeti/api";
    $.ajax({
            url: url,
            dataType: 'json'
        })
        .done(function(data) {
            //standarddaten
            var averagejourneys = data.average_journeys;
            var mostNumber = data.biggest_delay[0].name;
            var mostMinutes = data.biggest_delay[0].delay;
            var currentaverage = data.average_delay * 60;
            var currentaverageminutes = Math.floor(currentaverage / 60);
            var currentaverageseconds = currentaverage - currentaverageminutes * 60;
            var averagejourneys = data.journeys_delayed / data.current_journeys;
            averagejourneys = averagejourneys * 100;
            console.log([(data.current_journeys - data.journeys_delayed).toFixed(3), data.journeys_delayed.toFixed(3)])
            new Chart($('#train-percentage-chart')[0].getContext("2d"), {
                type: 'pie',
                data: {
                    labels: ['Pünktlich', 'Zu spät'],
                    datasets: [{
                        label: '# bei Berücksichtigen von 5 Minuten',
                        data: [(data.current_journeys - data.journeys_delayed).toFixed(3), data.journeys_delayed.toFixed(3)],
                        backgroundColor: [
							'rgba(50, 192, 50, 0.2)',
							'rgba(255, 99, 99, 0.2)'
                        ],
                        borderColor: [
							'rgba(50, 192, 50, 1)',
							'rgba(255, 99, 99, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                var dataset = data.datasets[tooltipItem.datasetIndex];
                                var meta = dataset._meta[Object.keys(dataset._meta)[0]];
                                var total = meta.total;
                                var currentValue = dataset.data[tooltipItem.index];
                                var percentage = parseFloat((currentValue / total * 100).toFixed(3));
                                return currentValue + ' (' + percentage + '%)';
                            },
                            title: function(tooltipItem, data) {
                                return data.labels[tooltipItem[0].index];
                            }
                        }
                    },
                }
            });
            $("#most-number").text(mostNumber);
            $("#most-minutes").text(mostMinutes);
            $("#average-minutes").text(currentaverageminutes);
            $("#average-seconds").text(currentaverageseconds);
        });
}
