fetch("data.json")
  .then((res) => res.json())
  .then((data) => {
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
      ],
      data['months'],
    ); // labels => months; values => monthly["type"]

    /*
    createChart(
      "activityChartYearly",
      "bar",
      [
        {
          label: "Walked (km)",
          data: years.map((y) => data.yearly[y].walked),
          backgroundColor: "#3B82F6",
        },
        {
          label: "Ran (km)",
          data: years.map((y) => data.yearly[y].ran),
          backgroundColor: "#EF4444",
        },
        {
          label: "Cycled (km)",
          data: years.map((y) => data.yearly[y].cycled),
          backgroundColor: "#10B981",
        },
      ],
      years,
    );
*/

    // (() => {
    //   createChart(
    //     "activityChartTotal",
    //     "bar",
    //     [
    //       {
    //         label: "Total (km)",
    //         data: [data.totals.walked, data.totals.ran, data.totals.cycled],
    //         backgroundColor: ["#3B82F6", "#EF4444", "#10B981"],
    //       },
    //     ],
    //     ["Walked", "Ran", "Cycled"],
    //   );
    // })/*()*/;

    // ...
  });
