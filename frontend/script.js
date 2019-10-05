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
			
			console.log(daten);
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


			$("#train-count").text(averagejourneys + "%");
			$("#most-number").text(mostNumber);
			$("#most-minutes").text(mostMinutes);
			$("#average").text(currentaverage);
		});
}
