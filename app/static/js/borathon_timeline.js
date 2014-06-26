
var timeline;

function initTimeline(div_id) {
    timeline = new links.Timeline(document.getElementById(div_id));
    return timeline;
}
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
        timeline = initTimeline(div_id);
        timeline.draw(log_array, options);
        addTimelineSelectionListener(onLogSelected);
    } else {
        timeline.setData(log_array);
        timeline.redraw();
    }
}

/**
 * Add a select listener for the timeline obj.
 * The listener function fhas the signature:
 * function onSelectFunc(data) {
 *    //the selected data is passed into this function.
 *    //data is one item such that {"content" : "xxxxx", "start" : 123423123"}
 * }
 * Smaple Code: 
 * addTimelineSelectionListener(function(item) {
 *    alert("You just selected: " + "Log Level: " + item.className + ". " + "\nDetail: " + item.content + "\n");
 *  });

 *
 */
function addTimelineSelectionListener(onSelectFunc) {
    if(timeline == null) {
        console.log("call initTimeline first.");
    } else {
        links.events.addListener(timeline, 'select', function() {
            var sel = timeline.getSelection();
            if (sel.length) {
                if (sel[0].row != undefined) {
                    var row = sel[0].row;
                    var item = timeline.getItem(row);
                    onSelectFunc(item);
                }
            }
        });
    }
}

function parseReturnedRawLogLines(result) {
    /* result looks like this: (...)
       1    #
       2   # A fatal error has been detected by the Java Runtime Environment:
       3  #
       4 #  SIGSEGV (0xb) at pc=0x00007fabf12a1f88, pid=3356, tid=140377072920320
       5    #
       6   # JRE version: Java(TM) SE Runtime Environment (7.0_40-b43) (build 1.7.0_40-b43)
       7  # Java VM: Java HotSpot(TM) 64-Bit Server VM (24.0-b56 mixed mode linux-amd64 compressed oops)
       8 # Problematic frame:
       9    # C  [libgtk-x11-2.0.so.0+0x13cf88]  gtk_menu_get_type+0x488
       */
    var result_pattern = /^\s+(\d+)\s+(.+)$/;
    var rawLogLines_inStr = result.split("\n");
    var i;
    var returnedArray = [];
    for(i = 0; i < rawLogLines_inStr.length; i++) {
        var rawLine = rawLogLines_inStr[i];
		  //alert("rawLine=" + rawLine);
        var match = result_pattern.exec(rawLine);
        if(match != null) {
            var lineNm = match[1];
            var content = match[2];
            returnedArray.push({line: match[1], content: match[2]});
        }
    }
    return returnedArray;
}

function onLogSelected(item) {
  //1. Get raw log information
  var filePath = item.source;
  var line = item.line;

 $.ajax({
     url: "raw",
     data: {linenum: line, file: filePath}
 }).done(function(result){
    var logLineArrays = parseReturnedRawLogLines(result);
    onRawLogLinesFetched(logLineArrays, line);
 });
 
  
  //2. Get bugzilla pr
}

// [{"id": 11, "summary": "XX"}, {"id": 22, "summary": "XX"}]

/**
 * The method is called when we have fetched a raw log lines inforamtion around the nth line.
 * loglines_array is a js array such that each element is an object:
 * {line: an int, content: a string}
 * it contains 2*n + 1 max lines.
 * n is current line number, which might need to be highlighted in html.
 */
function onRawLogLinesFetched(loglines_array, n) {
	$("#rawLogs").empty();
    for(var i = 0; i < loglines_array.length; i++) {
		var log_line = $("<li/>", {
		    "class": loglines_array[i].line == n ? "log-line exact-line" : "log-line", // you need to quote "class" since it's a reserved keyword
		    text: loglines_array[i].line + ":     " + loglines_array[i].content
		});
		
		$("#rawLogs").append(log_line);
    }
	
	$('#rawLogsModal').modal('show');
}
