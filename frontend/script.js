$(document).ready(function () {
	$("#body").hide();
	$("#loading").show();
	var url = "https://raw.githubusercontent.com/Jugendhackt/FahrplanDatenGarten/master/demo.json";
	$.ajax({
			url: url,
			dataType: 'json'
		})
		.done(function (data) {
			console.log(data);
			var currentdelayed = data.journeys_delayed;
			var mostNumber = data.biggest_delay[0].name;
			var mostMinutes = data.biggest_delay[0].delay;
			var currentaverage = data.average_delay;
			var averagejourneys = data.journeys_delayed / data.current_journeys;
			averagejourneys = Math.round(averagejourneys * 100);

			$("#train-count").text(averagejourneys + "%");
			$("#most-number").text(mostNumber);
			$("#most-minutes").text(mostMinutes);
			$("#average").text(currentaverage);
			$("#loading").fadeOut(function () {
				$("#body").fadeIn();
			});

			//console.log(averagejourneys);
		});

});
