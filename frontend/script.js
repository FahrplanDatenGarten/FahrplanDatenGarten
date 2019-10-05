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
	var zugformular = $("#zugformular");
	if (zugformular.length) {
		console.log("test");
		zugformular.closest('form').on('submit', function (e) {
			e.preventDefault();
			var daten = {};
			daten.date = $("input[name='date']").val();
			daten.startstation = $("input[name='startstation']").val();
			daten.endstation = $("input[name='endstation']").val();
			daten.starttime = $("input[name='starttime']").val();
			daten.endtime = $("input[name='endtime']").val();
			daten.arrivaldate = $("input[name='arrivaldate']").val();
			daten.arrivaltrain = $("input[name='arrivaltrain']").val();
			daten.arrivaltime = $("input[name='arrivaltime']").val();
			daten.firsttrainid = $("input[name='firsttrainid']").val();
			daten.firsttraintime = $("input[name='firsttraintime']").val();


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
						data: [data.journeys_delayed, data.current_journeys - data.journeys_delayed],
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
				},
				options: {
					tooltips: {
						callbacks: {
							label: function (tooltipItem, data) {
								var dataset = data.datasets[tooltipItem.datasetIndex];
								var meta = dataset._meta[Object.keys(dataset._meta)[0]];
								var total = meta.total;
								var currentValue = dataset.data[tooltipItem.index];
								var percentage = parseFloat((currentValue / total * 100).toFixed(1));
								return currentValue + ' (' + percentage + '%)';
							},
							title: function (tooltipItem, data) {
								return data.labels[tooltipItem[0].index];
							}
						}
					},
				}
			});
			$("#most-number").text(mostNumber);
			$("#most-minutes").text(mostMinutes);
			$("#average").text(currentaverage);
		});
}
