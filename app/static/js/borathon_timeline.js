
var timeline;
/**
 * 
 * Fill or redraw the timeline with updated log_array.
 * log array should has following format:
 * [{"content": "xxxx", "start": "a long number representing milliseconds from epoch", "className": "<optional>"},
 *  {"content": "xxxx", "start": "a long number", "className": "<optional>"},
 *  {"content": "xxxx", "start": "a long number", "className": "<optional>"},
 *  {"content": "xxxx", "start": "a long number", "className": "<optional>"}
 *  ]
 * div_id is id of the div that you expect draw the timeline there
 */
function fillTimeline(log_array, div_id) {
    // specify options
    var options = {
        "width":  "100%",
        //"scale": links.Timeline.StepDate.SCALE.MILLISECOND,
        //"step": 1,
        "axisOnTop": true,
        "cluster": true,
        "style": "dot" // optional
    };

    // $.each(json_result["entities"], function(idx, entity){
    // 	$.each(entity.logs, function(idx, log){
    // 		logs << log;
    // 	});
    // });
    // Instantiate our timeline object.
    // $.getJSON("hostd.log.json", function(data) {
    if(timeline == null) {
        timeline = new links.Timeline(document.getElementById(div_id));
        timeline.draw(log_array, options);
    } else {
        timeline.setData(log_array);
        timeline.redraw();
    }
    // Draw our timeline with the created data and options
    //alert("mlgb........");
    // });

}
