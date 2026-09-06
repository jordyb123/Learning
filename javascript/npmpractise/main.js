import dayjs from "dayjs";

const timeEl = document.getElementById("time");
const timezoneEl = document.getElementById("timezone");
const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
const dateEl = document.getElementById("date");
timezoneEl.textContent = zone;

function renderTime() {
    timeEl.textContent = dayjs().format("HH:mm:ss");
    dateEl.textContent = dayjs().format("dddd, D MMMM, YYYY");
}

renderTime();
setInterval(renderTime, 1000);