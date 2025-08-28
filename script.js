fetch("data.csv")
  .then((res) => res.text())
  .then((csvText) => {
    // Split CSV into rows
    const rows = csvText.trim().split("\n").map((r) => r.split(";"));

    const dataRows = rows;

    // Convert columns to arrays
    const data = {
      labels: dataRows.map((r) => r[0]),       // first column = labels
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
  });
