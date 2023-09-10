// Get the json data from localhost:39847
$(document).ready(function () {
    var jsonData;
    var chart;
    var pieSeries;

    $.ajax({
        url: 'http://localhost:39847',
        dataType: 'json',
        success: function (data) {
            // Print the data
            console.log(data);
            jsonData = data;
            /**
             * ---------------------------------------
             * This demo was created using amCharts 4.
             * 
             * For more information visit:
             * https://www.amcharts.com/
             * 
             * Documentation is available at:
             * https://www.amcharts.com/docs/v4/
             * ---------------------------------------
             */
        
            // Themes begin
            am4core.useTheme(am4themes_animated);
            // Themes end
        
            // Create chart instance
            chart = am4core.create("chartdiv", am4charts.PieChart);
        
            // Add data
            var executionTimes = jsonData.executionTimes;
            // First convert the executions times to data that amCharts can use
            var data = [];
            for (var key in executionTimes) {
                if(key != "all")
                {
                    if (executionTimes.hasOwnProperty(key)) {
                        var value = executionTimes[key];
                        data.push({
                            name: key,
                            value: value
                        });
                    }
                }
            }
        
            chart.data = data;
            console.log(executionTimes);

            // Add and configure Series
            pieSeries = chart.series.push(new am4charts.PieSeries());
            pieSeries.dataFields.value = "value";
            pieSeries.dataFields.category = "name";
            pieSeries.slices.template.stroke = am4core.color("#fff");
            pieSeries.slices.template.strokeWidth = 2;
            pieSeries.slices.template.strokeOpacity = 1;
        }
    });

    // Update the table every 0.1 seconds
    setInterval(function () {
        $.ajax({
            url: 'http://localhost:39847',
            dataType: 'json',
            success: function (data) {
                // Print the data
                console.log(data.executionTimes);
                jsonData = data;
                /**
                 * ---------------------------------------
                 * This demo was created using amCharts 4.
                 * 
                 * For more information visit:
                 * https://www.amcharts.com/
                 * 
                 * Documentation is available at:
                 * https://www.amcharts.com/docs/v4/
                 * ---------------------------------------
                 */
            
                // Themes begin
                am4core.useTheme(am4themes_animated);
                // Themes end
            
            
                // Add data
                var executionTimes = jsonData.executionTimes;
                // First convert the executions times to data that amCharts can use
                var data = [];
                var all0 = true;
                for (var key in executionTimes) {
                    if(key != "all")
                    {
                        if (executionTimes.hasOwnProperty(key)) {
                            var value = executionTimes[key];
                            if(value != 0)
                            {
                                all0 = false;
                            }
                            data.push({
                                name: key,
                                value: value
                            });
                        }
                    }
                }
                if(!all0)
                {
                    // Smoothly transition the pie chart to the new data
                    chart.data = data;
                }
            
            }
        });
    }, 100);
});
