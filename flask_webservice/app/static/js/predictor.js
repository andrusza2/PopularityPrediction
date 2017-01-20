function update(result, nanobar, status_div) {
    // update UI
    percent = 100;
    nanobar.go(percent);
    $(status_div.childNodes[1]).text(percent + '%');
    //$(status_div.childNodes[2]).text(data['status']);

    $(status_div.childNodes[3]).text('Result: ' + result)


}
function update_progress(status_url, nanobar, status_div) {
    // send GET request to status URL
    $.getJSON(status_url, function (data) {
        // update UI
        percent = parseInt(data['current'] * 100 / data['total']);
        nanobar.go(percent);
        $(status_div.childNodes[1]).text(percent + '%');
        $(status_div.childNodes[2]).text(data['status']);
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {

                    var start_panel = $("#content-start");
                    var progress_panel = $("#content-progress");
                    var result_panel = $("#content-result");

                var result = $("#content-result-div");
                
                drawPredictionChart(data['result']['first'], data['result']['pref']);

                var newheight = 350;

                var newheight = result_panel.height() + 20;
                
                $(result_panel).css("display", "block");

                $(progress_panel).stop().animate({
                    "left": "-880px"
                }, 800, function () { /* callback */
                });

                $(result_panel).stop().animate({
                    "left": "0px"
                }, 800, function () {
                    $(progress_panel).css("display", "none");
                });

                $("#page").stop().animate({
                    "height": newheight + "px"
                }, 550, function () { /* callback */
                });


            }
            else {
                // something unexpected happened
                $(status_div.childNodes[3]).text('Result: ' + data['state']);
            }
        }
        else {
            // rerun in 2 seconds
            setTimeout(function () {
                update_progress(status_url, nanobar, status_div);
            }, 1000);
        }
    });
}

function start_long_task() {

    var start_panel = $("#content-start");
    var progress_panel = $("#content-progress");
    var result_panel = $("#content-result");


    var newheight = start_panel.height();

    $(progress_panel).css("display", "block");

    $(start_panel).stop().animate({
        "left": "-880px"
    }, 800, function () { /* callback */
    });

    $(progress_panel).stop().animate({
        "left": "0px"
    }, 800, function () {
        $(start_panel).css("display", "none");
    });

    $("#page").stop().animate({
        "height": newheight + "px"
    }, 550, function () { /* callback */
    });

    var formData = new FormData($("form#my_form")[0]);

    // send ajax POST request to start background job
    $.ajax({
        type: 'POST',
        url: '/longtask',
        data: formData,
        contentType: false,
        processData: false,
        success: function (data, status, request) {
            status_url = request.getResponseHeader('Location');
            image_url = request.getResponseHeader('Thumbnail');

            var img = document.createElement('img');
            img.className = "thumbnail";
            img.src = image_url;
            img.style.width = '100%';


            $('#progress').append(img);

            // $('#result').append(img);
            $('#thumbnail-place').append(img);

            // add task status elements
            div = $('<div class="trr"><div></div><div>0%</div><div>...</div><div>&nbsp;</div></div>');
            $('#progress').append(div);
            // create a progress bar
            var nanobar = new Nanobar({
                bg: '#44f',
                target: div[0].childNodes[0]
            });

//                    update(data['result']['result'], nanobar, div[0]);

            update_progress(status_url, nanobar, div[0]);
        },
        error: function () {
            alert('Unexpected error');
        }
    });
}

$(document).ready(function () {
    $("form").submit(function (e) {
        e.preventDefault();
    });

    var start_panel = $("#content-start");
    var result_panel = $("#content-result");
    var progress_panel = $("#content-progress");

    /* display the login page */
    $("#showstart").on("click", function (e) {
        e.preventDefault();

        // $('#progress').clone().prependTo("#history");
        // $('#progress').text("");

        $('<hr>').prependTo("#history");
        $('#result').clone().prependTo("#history");
        // $('#result').text("");
        $('#thumbnail-place').text("");
        $('#content-result-div').text("");

        $('#progress').text("");
        $('#content-history').css("display", "block");


        var newheight = start_panel.height();
        $(start_panel).css("display", "block");

        $(start_panel).stop().animate({
            "left": "0px"
        }, 800, function () { /* callback */
        });
        $(result_panel).stop().animate({
            "left": "880px"
        }, 800, function () {
            $(result_panel).css("display", "none");
        });

        $(progress_panel).css("left", "880px");
        // $(progress_panel).style.left = "880px";

        $("#page").stop().animate({
            "height": newheight + "px"
        }, 550, function () { /* callback */
        });
    });
});