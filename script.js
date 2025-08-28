fetch("data.csv")
  .then((res) => res.text())
  .then((csvText) => {
    // Split CSV into rows
    const rows = csvText
      .trim()
      .split("\n")
      .map((r) => r.split(";"));

    const dataRows = rows;

    // Convert columns to arrays
    const data = {
      labels: dataRows.map((r) => {
        const d = new Date(r[0]);
        return d.toLocaleString("de-DE", { month: "short", year: "numeric" });
      }), // first column = labels
      walked: dataRows.map((r) => parseFloat(r[1])),
      ran: dataRows.map((r) => parseFloat(r[2])),
      cycled: dataRows.map((r) => parseFloat(r[3])),
    };

    console.log(data);

    const ctx = document.getElementById("activityChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Walked (km)",
            data: data.walked,
            borderColor: "#3B82F6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Ran (km)",
            data: data.ran,
            borderColor: "#EF4444",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Cycled (km)",
            data: data.cycled,
            borderColor: "#10B981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });

    const totals = { walked: 0, ran: 0, cycled: 0 };

    rows.forEach((r) => {
      totals.walked += parseFloat(r[1]?.replace(",", ".") || 0);
      totals.ran += parseFloat(r[2]?.replace(",", ".") || 0);
      totals.cycled += parseFloat(r[3]?.replace(",", ".") || 0);
    });

    const ctx_total = document
      .getElementById("activityChartTotal")
      .getContext("2d");
    new Chart(ctx_total, {
      type: "bar",
      data: {
        labels: ["Walked", "Ran", "Cycled"],
        datasets: [
          {
            label: "Total (km)",
            data: [totals.walked, totals.ran, totals.cycled],
            backgroundColor: ["#3B82F6", "#EF4444", "#10B981"],
          },
        ],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });
  });
