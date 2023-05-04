moment.locale('pt-BR');

export function create_doughnut(chart_id, label_1, label_2, data_1, data_2, title, fields, other_datasets=null, label_main_dataset="") {
    let datasets = []
    if (other_datasets != null) {
        for (let i = 0; i < other_datasets.length; i++){
            let total_sum = 0;
            for(let j = 0; j < fields.length; j++){ total_sum += other_datasets[i]["total_sum"][fields[j]] }
            let dataset = {
                backgroundColor: ["rgba(50, 103, 255, 0.75)", "rgba(50, 103, 255, 0.25)"],
                borderColor: ["rgb(50, 103, 255)", "rgb(50, 103, 255)"],
                borderWidth: 1,
                weight: 100,
                data: [data_1, (data_1 >= total_sum) ? 0 : total_sum - data_1],
                label: other_datasets[i]["funding"]
            };
            datasets.push(dataset)
        }
    }
    let main_dataset = {
        backgroundColor: ["rgba(50, 103, 255, 0.75)", "rgba(50, 103, 255, 0.25)"],
        borderColor: ["rgb(50, 103, 255)", "rgb(50, 103, 255)"],
        borderWidth: 1,
        weight: 100,
        data: [data_1, (data_1 >= data_2) ? 0 : data_2 - data_1],
        label: label_main_dataset
    };

    datasets.push(main_dataset);

    new Chart(chart_id, {
        type: "doughnut",
        data: {
            labels: [label_1, label_2],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1,
            legend: {display: false},
            scales: {y: {display: false}},
            title: {
                display: true,
                text: title
            },
            plugins: {
                labels: {
                    fontColor: 'black'
                },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            return `${tooltipItems[0].label}`;
                        },
                    }
                },
            },
        }
    });
}

export function create_timeline(chart_id, data, xAxesLabel, yAxesLabel, project, title) {
    new Chart(chart_id, {
        type: "line",
        data: {
            datasets: [
                {
                    label: project,
                    backgroundColor: ["rgba(50, 103, 255, 0.75)", "rgba(50, 103, 255, 0.25)"],
                    borderColor: ["rgb(50, 103, 255)", "rgb(50, 103, 255)"],
                    borderWidth: 1,
                    data: data, // [{"x":yyyy-mm-dd, "y":int, "label": name of the activity}]
                    tension: 0,
                    fill: 'origin',
                    pointBackgroundColor: "rgb(0, 0, 0)"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            aspectRatio: 2,
            legend: {display: false},
            locale: "pt-BR",
            scales: {
                x: {
                    scaleLabel: {
                        display: true,
                        labelString: xAxesLabel
                    },
                    type: "time",
                    time: {
                        unit: "month",
                        displayFormats: {
                            month: "MMMM, YYYY"
                        }
                    }
                },
                y: {
                    scaleLabel: {
                        display: true,
                        labelString: yAxesLabel
                    },
                    ticks: {
                        beginAtZero: true
                    }
                },
            },
            plugins: {
                title: {
                    display: false,
                    text: title
                },
                tooltip: {
                    callbacks: {
                        title: function (tooltipItem) {
                            return tooltipItem[0].dataset.label;
                        },
                        label: function (tooltipItem) {
                            let dataset = tooltipItem.dataset;
                            let currentIndex = tooltipItem.dataIndex;
                            let currentPoint = dataset.data[currentIndex];
                            let currentValue = currentPoint.y;
                            let previousValue = currentIndex > 0 ? dataset.data[currentIndex - 1].y : currentValue;
                            let valueDiff = currentValue - previousValue;
                            return valueDiff > 0 ? `${currentPoint.label}: ${currentValue} (+${valueDiff})` : `${currentPoint.label}: ${currentValue}`;
                        }
                    }
                }
            }
        }
    });
}

