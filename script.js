const YEARLY_GOALS = [
  { year: "2024", text: "walk + run 1000km in total", progress: { activity: ["walked", "ran"], target: 1000 } },
  { year: "2025", text: "walk 1000km", progress: { activity: "walked", target: 1000 } },
  { year: "2026", text: "run 667 km", progress: { activity: "ran", target: 667 } },
];

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

fetch("data.json")
  .then((res) => res.json())
  .then((data) => {
    const renderGoals = (goals) => {
      const list = document.getElementById("yearlyGoals");

      goals.forEach((goal, i) => {
        const activities = [].concat(goal.progress.activity);
        const target = goal.progress.target;
        // sum across multiple activities for combo goals, e.g. walked + ran
        const achieved = activities.reduce((sum, activity) => sum + (data["yearly"][activity][goal.year] || 0), 0);
        const remaining = Math.max(target - achieved, 0);
        const percent = ((achieved / target) * 100).toFixed(1);
        const done = achieved >= target;

        const li = document.createElement("li");
        li.className = "bg-white p-3 rounded shadow";
        li.innerHTML = `
          <div class="flex items-center">
            <span class="${done ? "text-green-500" : "text-gray-400"} mr-2">${done ? "✔" : "○"}</span>
            <span>${goal.year} &middot; ${goal.text}</span>
          </div>
          ${done ? "" : `<canvas id="goalProgress-${i}" height="10" class="mt-2"></canvas>`}
        `;
        list.appendChild(li);

        if (!done) {
            new Chart(document.getElementById(`goalProgress-${i}`).getContext("2d"), {
              type: "bar",
              data: {
                labels: [goal.year],
                datasets: [
                  { label: "Done", data: [achieved], backgroundColor: "#EF4444" },
                  { label: "Remaining", data: [remaining], backgroundColor: "#E5E7EB" },
                ],
              },
              options: {
                indexAxis: "y",
                responsive: true,
                scales: {
                  x: { stacked: true, max: target, display: false },
                  y: { stacked: true, display: false },
                },
                plugins: {
                  legend: { display: false },
                  tooltip: { enabled: false },
                  title: { display: false },
                  centerLabel: { text: `${achieved.toFixed(1)} / ${target} km (${percent}%)` },
                },
              },
            });
        }
      });
    };

    renderGoals(YEARLY_GOALS);

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
          label: "Swam (km)",
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
          label: "Swam (km)",
          data: data['yearly']['swam'],
          backgroundColor: "#F59E0B",
        },
      ],
      data['years'],
    );

  });
