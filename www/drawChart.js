var ctx = document.getElementById("myChart");
var parent = document.getElementById("wykres");
ctx.width = parent.offsetWidth;
ctx.height = parent.offsetHeight;
var myChart = null;

function draw() {

    $.ajax({
        cache: false,
        url: "voltages.json",
        dataType: "json",
        success: function(jsonData) {
            
            document.getElementById("currV").innerHTML = "V: " + jsonData["currentVoltage"] + " V (" + jsonData["currentTimestamp"] + ")"
            document.getElementById("maxV").innerHTML = "V max: " + jsonData["maxVoltage"] + " V (" + jsonData["maxVoltageTimestamp"] + ")"
            document.getElementById("minV").innerHTML = "V min: " + jsonData["minVoltage"] + " V (" + jsonData["minVoltageTimestamp"] + ")"

            // document.getElementById("wykres").innerHTML = jsonData["voltage"][0]["x"]
            
            var voltages = jsonData["voltage"].map(a => a.y);
            var maxChartVoltage = Math.max(...voltages);
            var minChartVoltage = Math.min(...voltages);

            if (myChart != null) {
                myChart.destroy();
            }
            myChart = new Chart(ctx, {
                type: "line",
                data: {
                    datasets: [{
                        label: "Napięcie[V]",
                        data: jsonData["voltage"],
                        fill: false,
                        borderColor: "rgb(0, 0, 0)",
                        borderWidth: 1.1,
                        lineTension: 0,
                        pointRadius: 0
                    }]
                },

                options: {
                    animation: {
                        duration: 0
                    },
                    responsive: false,
                    maintainAspectRatio: false,
                    scales: {
                        xAxes: [{
                            type: "time",
                            distribution: "linear",
                            time: {
                                parser: function (utcMoment) {
                                    return moment(utcMoment - 1000*60*60*2); //hack: subtract 2 hours to prevent timezone application
                                },
                                unit: "minute",
                                displayFormats: {
                                    minute: "HH:mm",
                                },
                                min: jsonData["voltage"][0]["x"],
                                max: jsonData["voltage"][0]["x"] + 1000*60*60*24,
                                stepSize: 60
                            }
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: false,
                                stepSize: 1,
                                min: 235, //minChartVoltage - 5,
                                max: 247, //maxChartVoltage + 5,
                            }
                        }]
                    }
                }
            });
        }
    });

    setTimeout(draw, 10000);
}

draw();

