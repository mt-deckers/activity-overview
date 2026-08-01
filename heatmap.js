// Renders the active-calories "heat" calendar (GitHub-contributions style) from the
// abstracted calories.json. The JSON carries only date/color/highlight — never a raw
// calorie number — so nothing here can leak the underlying values.

const DAY_MS = 86400000;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Mon", "", "Wed", "", "Fri", "", ""]; // label Mon/Wed/Fri like GitHub

// Parse "YYYY-MM-DD" as a local date (avoids UTC off-by-one shifts).
const parseDate = (s) => {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
};
const iso = (dt) => `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
// Monday-first weekday index: Mon=0 … Sun=6.
const weekday = (dt) => (dt.getDay() + 6) % 7;

fetch("calories.json")
  .then((res) => res.json())
  .then((data) => {
    const root = document.getElementById("caloriesHeatmap");
    if (!data.days || !data.days.length) {
      root.textContent = "No calorie data yet.";
      return;
    }

    const byDate = new Map(data.days.map((d) => [d.date, d]));
    const start = parseDate(data.start);
    const end = parseDate(data.end);

    // Pad to whole weeks: grid starts on the Monday on/before start, ends on the
    // Sunday on/after end, so every column is a full 7-day stack.
    const gridStart = new Date(start);
    gridStart.setDate(gridStart.getDate() - weekday(start));
    const gridEnd = new Date(end);
    gridEnd.setDate(gridEnd.getDate() + (6 - weekday(end)));
    const nWeeks = Math.round((gridEnd - gridStart) / DAY_MS + 1) / 7;

    const hm = document.createElement("div");
    hm.className = "hm";

    // --- month labels: one per week-column where the month changes ---
    const months = document.createElement("div");
    months.className = "hm-months";
    months.style.gridTemplateColumns = `repeat(${nWeeks}, calc(var(--cell) + var(--gap)))`;
    let prevMonth = -1;
    for (let w = 0; w < nWeeks; w++) {
      const colDate = new Date(gridStart.getTime() + w * 7 * DAY_MS);
      if (colDate.getMonth() !== prevMonth) {
        prevMonth = colDate.getMonth();
        const label = document.createElement("span");
        label.textContent = MONTHS[prevMonth];
        label.style.gridColumn = `${w + 1} / span 4`;
        months.appendChild(label);
      }
    }

    // --- weekday labels (left rail) ---
    const weekdays = document.createElement("div");
    weekdays.className = "hm-weekdays";
    WEEKDAYS.forEach((w) => {
      const el = document.createElement("div");
      el.textContent = w;
      weekdays.appendChild(el);
    });

    // --- day cells, column-major (sequential days fill each 7-row column) ---
    const grid = document.createElement("div");
    grid.className = "hm-grid";
    const totalDays = Math.round((gridEnd - gridStart) / DAY_MS) + 1;
    for (let i = 0; i < totalDays; i++) {
      const dt = new Date(gridStart.getTime() + i * DAY_MS);
      const cell = document.createElement("div");
      cell.className = "hm-cell";

      // Anything without a value — outside the range or a no-data day — stays blank
      // (renders nothing); only days with data get a filled, outlined cell.
      const day = dt >= start && dt <= end ? byDate.get(iso(dt)) : undefined;
      if (day) {
        cell.classList.add("filled");
        cell.style.background = day.color;
        if (day.highlight) {
          cell.classList.add("hm-mega");
          cell.title = `${day.date} · 🔥 MEGA day`;
        } else {
          cell.title = day.date;
        }
      }
      grid.appendChild(cell);
    }

    const scroll = document.createElement("div");
    scroll.className = "hm-scroll";
    scroll.appendChild(months);
    scroll.appendChild(grid);

    const wrap = document.createElement("div");
    wrap.className = "hm-wrap";
    wrap.appendChild(weekdays);
    wrap.appendChild(scroll);
    hm.appendChild(wrap);

    // --- legend + mega counter ---
    const legend = document.createElement("div");
    legend.className = "hm-legend";
    const items = [
      ["#6b7280", "under the weather · 1–599"],
      ["#3b82f6", "cruising · 600–899"],
      ["#ef4444", "putting in work · 900–1400"],
      ["#fde047", "🔥 MEGA · >1400", true],
    ];
    items.forEach(([color, label, mega]) => {
      const item = document.createElement("span");
      item.className = "item";
      const sw = document.createElement("span");
      sw.className = "sw" + (mega ? " mega" : "");
      sw.style.background = color;
      item.appendChild(sw);
      item.appendChild(document.createTextNode(label));
      legend.appendChild(item);
    });
    hm.appendChild(legend);

    const counter = document.createElement("div");
    counter.className = "hm-legend";
    counter.innerHTML = `<span class="hm-count">🔥 ${data.megaCount} mega days</span> out of ${data.days.length} logged`;
    hm.appendChild(counter);

    root.innerHTML = "";
    root.appendChild(hm);
  });
