// Chart.js has no built-in way to draw a label inside a bar, so draw it manually
Chart.register({
  id: "centerLabel",
  afterDatasetsDraw(chart) {
    const text = chart.options.plugins.centerLabel?.text;
    if (!text) return;
    const { ctx, chartArea } = chart;
    ctx.save();
    ctx.font = "12px sans-serif";
    ctx.fillStyle = "#111827";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, chartArea.left + chartArea.width / 2, (chartArea.top + chartArea.bottom) / 2);
    ctx.restore();
  },
});

Promise.all([
  fetch("data/data.json").then((res) => res.json()),
  fetch("data/goals.json").then((res) => res.json()),
])
  .then(([data, goals]) => {
    const renderGoals = (goals) => {
      const list = document.getElementById("goals");

      goals.forEach((goal, i) => {
        const { activity, target, completed, done: explicitDone } = goal.progress;
        // a yearly goal derives its value from the activity data; a dated one states it
        const isYearly = activity !== undefined;
        const label = isYearly ? goal.year : goal.date;
        const unit = goal.unit ?? "km";

        let achieved, done;
        if (isYearly) {
          // sum across multiple activities for combo goals, e.g. walked + ran
          achieved = [].concat(activity).reduce((sum, a) => sum + (data["yearly"][a][goal.year] || 0), 0);
          done = achieved >= target;
        } else {
          achieved = completed;
          // only comparable numbers can decide this for us; otherwise the file says so
          done =
            typeof achieved === "number" && typeof target === "number"
              ? achieved >= target
              : explicitDone === true;
        }

        const numeric = typeof achieved === "number" && typeof target === "number";
        // a finished yearly goal drops its bar; a dated one keeps it, so >100% stays visible
        const showBar = numeric && !(isYearly && done);
        // a dated goal with no bar prints its result verbatim, met or missed
        const note = !isYearly && !showBar && achieved !== undefined ? achieved : null;

        const li = document.createElement("li");
        li.className = "bg-white p-3 rounded shadow";
        li.innerHTML = `
          <div class="flex items-center">
            <span class="${done ? "text-green-500" : "text-gray-400"} mr-2">${done ? "✔" : "○"}</span>
            <span>${label} &middot; ${goal.text}</span>
          </div>
          ${showBar ? `<canvas id="goalProgress-${i}" height="10" class="mt-2"></canvas>` : ""}
          ${note === null ? "" : `<div class="mt-1 text-sm text-gray-600">${note}</div>`}
        `;
        list.appendChild(li);

        if (showBar) {
          const remaining = Math.max(target - achieved, 0);
          const percent = ((achieved / target) * 100).toFixed(1);
          // an over-target bar fills the whole track, in green rather than part-red
          const over = achieved >= target;

            new Chart(document.getElementById(`goalProgress-${i}`).getContext("2d"), {
              type: "bar",
              data: {
                labels: [label],
                datasets: over
                  ? [{ label: "Done", data: [achieved], backgroundColor: "#10B981" }]
                  : [
                      { label: "Done", data: [achieved], backgroundColor: "#EF4444" },
                      { label: "Remaining", data: [remaining], backgroundColor: "#E5E7EB" },
                    ],
              },
              options: {
                indexAxis: "y",
                responsive: true,
                scales: {
                  x: { stacked: true, max: Math.max(target, achieved), display: false },
                  y: { stacked: true, display: false },
                },
                plugins: {
                  legend: { display: false },
                  tooltip: { enabled: false },
                  title: { display: false },
                  centerLabel: { text: `${achieved.toFixed(1)} / ${target} ${unit} (${percent}%)` },
                },
              },
            });
        }
      });
    };

    renderGoals(goals);

    const createChart = (ctxId, type, datasets, labels = data.labels) => {
      const ctx = document.getElementById(ctxId).getContext("2d");
      new Chart(ctx, {
        type,
        data: { labels, datasets },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
      });
    };

    createChart(
      "activityChart",
      "line",
      [
        {
          label: "Walked (km)",
          data: data['monthly']['walked'],
          borderColor: "#3B82F6",
          backgroundColor: "rgba(59,130,246,0.1)",
          fill: true,
          tension: 0.3,
        },
        {
          label: "Ran (km)",
          data: data['monthly']['ran'],
          borderColor: "#EF4444",
          backgroundColor: "rgba(239,68,68,0.1)",
          fill: true,
          tension: 0.3,
        },
        {
          label: "Cycled (km)",
          data: data['monthly']['cycled'],
          borderColor: "#10B981",
          backgroundColor: "rgba(16,185,129,0.1)",
          fill: true,
          tension: 0.3,
        },
        {
          label: "Swam (hours)",
          data: data['monthly']['swam'],
          borderColor: "#F59E0B",
          backgroundColor: "rgba(245,158,11,0.1)",
          fill: true,
          tension: 0.3,
        },
      ],
      data['months'],
    ); // labels => months; values => monthly["type"]

    createChart(
      "activityChartYearly",
      "bar",
      [
        {
          label: "Walked (km)",
          data: data['yearly']['walked'],
          backgroundColor: "#3B82F6",
        },
        {
          label: "Ran (km)",
          data: data['yearly']['ran'],
          backgroundColor: "#EF4444",
        },
        {
          label: "Cycled (km)",
          data: data['yearly']['cycled'],
          backgroundColor: "#10B981",
        },
        {
          label: "Swam (hours)",
          data: data['yearly']['swam'],
          backgroundColor: "#F59E0B",
        },
      ],
      data['years'],
    );

  });
