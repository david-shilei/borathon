// var myObject = eval('(' + myJSONtext + ')');
// var myJSONText = JSON.stringify(myObject, replacer);
// function replacer(key, value) {
//     if (typeof value === 'number' && !isFinite(value)) {
//         return String(value);
//     }
//     return value;
// }
var json_result = {
"entities": [
 	{
		"name": "host-9:91:76e1b7f8-0-13e9",
		"logs": [ 
			{
				"start": 1231231231123,
				"line": 234,
				"file": "hostd.log",
 			    "content":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
			}]
	},
	{
		"name": "host-9:94:22480d43-0-1ae8",
		"logs": [
			{
				"start": 1231231231231,
				"line": 235,
				"file": "hostd.log",
				"content": "2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
			}]
	}
]}

$(document).ready(function(){	
	var data = [{"content":"RecordOp ASSIGN: guest, 53. Sent notification immediately.","loglevel":"verbose","start":1399706542422},{"content":"RecordOp ASSIGN: summary.guest, 17. Sent notification immediately.","loglevel":"verbose","start":1399706546913},{"content":"Done Dispatching Vigor callback","loglevel":"verbose","start":1399706556078}]
	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
	data = data.slice(0, 5)
  	$.each(json_result["entities"], function(idx, entity){
		var link = $("<a />", {
		    href: "#",
		    "class": "entity-link", // you need to quote "class" since it's a reserved keyword
		    text: entity.name,
			title: entity.name,
			style: "float:left"
		});
		link.data("name", entity.name);
		link.data("logs", entity.logs);
		
		var badge = $("<span />", {
			"class": "badge",
			text: entity.logs.length,
			style: "float:right"
		});
		
		var newItem = $("<li />", {
		    style: "display: none; clear: both;"
		});
		newItem.append(link);
		newItem.append(badge);
		
		newItem.appendTo($("#entityList")).show('slow');
  	});
	  
  	$(".entity-link").click(function(){
		var log = $(this).data("logs")[0]
  		displayLog(log);
  	});
});

function displayLog(log) {
	var contentContainer = $('#entityContent');
	contentContainer.empty();
    var logContent = $('<div class="span4" style="display: none;"><h2>' + new Date(log.start) +'</h2><p>' +  log.content + '</p></div><!--/span-->');
	logContent.appendTo(contentContainer).show('slow');
}


$(document).ready(function () { 
    // specify options
    var options = {
        "width":  "100%",
        //"scale": links.Timeline.StepDate.SCALE.MILLISECOND,
        //"step": 1,
        "axisOnTop": true,
        "cluster": true,
        "style": "dot" // optional
    };
	
	logs = json_result["entities"][0].logs;
	// $.each(json_result["entities"], function(idx, entity){
	// 	$.each(entity.logs, function(idx, log){
	// 		logs << log;
	// 	});
	// });

        // Instantiate our timeline object.
        // $.getJSON("hostd.log.json", function(data) {
            var timeline = new links.Timeline(document.getElementById('mytimeline'));
            // Draw our timeline with the created data and options
            //alert("mlgb........");
            timeline.draw(logs, options);
        // });

    });