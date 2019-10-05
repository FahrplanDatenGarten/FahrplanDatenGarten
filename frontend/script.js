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
		standartdaten();
		pageload();
		formular();
	});


}

function pageload() {
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

}

function formular() {
	console.log("123");
	var zugformular = $("#zugformular");
	if (zugformular.length) {
		console.log("test");
		zugformular.closest('form').on('submit', function (e) {

			console.log("Hello");
			e.preventDefault();

		});
	}

}

function standartdaten() {
	var url = "https://raw.githubusercontent.com/Jugendhackt/FahrplanDatenGarten/master/demo.json";
	$.ajax({
		url: url,
		dataType: 'json'
	})
		.done(function (data) {
			console.log(data);
			//standarddaten
			var averagejourneys = data.average_journeys;
			var mostNumber = data.biggest_delay[0].name;
			var mostMinutes = data.biggest_delay[0].delay;
			var currentaverage = data.average_delay;
			var averagejourneys = data.journeys_delayed / data.current_journeys;
			averagejourneys = (averagejourneys * 100).toFixed(2);
			new Chart($('#train-procent-chart')[0].getContext("2d"), {
				type: 'pie',
				data: {
					labels: ['Pünktlich', 'Zu spät'],
					datasets: [{
						label: '# bei Berücksichtigen von 5 Minuten',
						data: [averagejourneys, 100 - averagejourneys],
						backgroundColor: [
							'rgba(75, 192, 192, 0.2)',
							'rgba(255, 99, 132, 0.2)'
						],
						borderColor: [
							'rgba(75, 192, 192, 1)',
							'rgba(255, 99, 132, 1)'
						],
						borderWidth: 1
					}]
				}
			});
			new Chart($('#train-absolute-chart')[0].getContext("2d"), {
				type: 'pie',
				data: {
					labels: ['Pünktlich', 'Zu spät'],
					datasets: [{
						label: '# bei Berücksichtigen von 5 Minuten',
						data: [averagejourneys, 100 - averagejourneys],
						backgroundColor: [
							'rgba(75, 192, 192, 0.2)',
							'rgba(255, 99, 132, 0.2)'
						],
						borderColor: [
							'rgba(75, 192, 192, 1)',
							'rgba(255, 99, 132, 1)'
						],
						borderWidth: 1
					}]
				}
			});
			$("#most-number").text(mostNumber);
			$("#most-minutes").text(mostMinutes);
			$("#average").text(currentaverage);
		});
}
