// Bulma Calendar
bulmaCalendar.attach('[type="date"]', {
    dateFormat: "YYYY-MM-DD",
    weekStart: 1,
    showHeader: false,
    showFooter: false
});


time_picker = bulmaCalendar.attach('[type="time"]', {
    timeFormat: "HH:MM",
    weekStart: 1,
    displayMode: "dialog",
    minuteSteps: 1,
    showHeader: false,
    validateLabel: "Save",
    showClearButton: false,
    showTodayButton: false,
    closeOnOverlayClick: false,
});

time_calendar_elements = document.getElementsByClassName("calendar-time-prefill")
for (let i = 0; i < time_calendar_elements.length; i++) {
    let el = time_calendar_elements[i]
    if (el.dataset.value !== undefined) {
        el.bulmaCalendar.time.start = new Date(el.dataset.value);
        el.bulmaCalendar.save();
        el.bulmaCalendar.refresh()
    }
}

date_calendar_elements = document.getElementsByClassName("calendar-date-prefill")
for (let i = 0; i < date_calendar_elements.length; i++) {
    let el = date_calendar_elements[i]
	if (el.dataset.value !== undefined && el.dataset.value !== "None") {
		el.bulmaCalendar.date.start = new Date(el.dataset.value);
		el.bulmaCalendar.save();
		el.bulmaCalendar.refresh()
	}
}
