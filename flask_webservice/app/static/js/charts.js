// Load the Visualization API and the corechart package.
google.charts.load('current', {'packages': ['corechart']});

// // Set a callback to run when the Google Visualization API is loaded.
// google.charts.setOnLoadCallback(drawChart);

// Callback that creates and populates a data table,
// instantiates the column chart, passes in the data and
// draws it.
function drawPredictionChart(first_thumbnail_result, pref_thumbnail_result) {

    // Create the data table.
    var data = google.visualization.arrayToDataTable([
        ['Result', 'Popularity Score'],
        ['First Thumbnail', first_thumbnail_result],
        ['Preferred Thumbnail', pref_thumbnail_result],
    ]);

    // Set chart options
    var options = {
        'title': 'Popularity Prediction',
        'width': 350,
        'height': 350,
        'animation': {
            'startup': true,
            'duration': 1500,
        },
        'legend': { position: 'none' },
        'vAxis': {
            minValu: 0,
            maxValue: 10,
            ticks: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
          }
    };

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.ColumnChart(document.getElementById('content-result-div'));
    chart.draw(data, options);
}
