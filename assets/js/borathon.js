// var myObject = eval('(' + myJSONtext + ')');
// var myJSONText = JSON.stringify(myObject, replacer);
// function replacer(key, value) {
//     if (typeof value === 'number' && !isFinite(value)) {
//         return String(value);
//     }
//     return value;
// }
var json_result = {
		"host-9:91:76e1b7f8-0-13e9": [ 
			{
				"start": 1231231231123,
				"line": 234,
				"file": "hostd.log",
 			    "content":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
			}],
		"host-9:94:22480d43-0-1ae8": [
			{
				"start": 1231231231231,
				"line": 235,
				"file": "hostd.log",
				"content": "2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
			}]
}

$(document).ready(function(){	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
  	buildEntitiesList(json_result);
});

function buildEntitiesList(entities) {
	var logsToTimeline = []
  	for(var entityName in entities) {
		var logs = entities[entityName];
		// TODO
		logsToTimeline = logs;
		var link = $("<a />", {
		    href: "#",
		    "class": "entity-link", // you need to quote "class" since it's a reserved keyword
		    text: entityName,
			title: entityName,
			style: "float:left"
		});
		link.data("name", entityName);
		link.data("logs", logs);
		
	  	link.click(function(){
			var entityName = $(this).data("name");
			filterEntity(entityName);
			var log = $(this).data("logs")[0];
	  		displayLog(log);
	  	});
		
		var badge = $("<span />", {
			"class": "badge",
			text: logs.length,
			style: "float:right"
		});
		
		var newItem = $("<li />", {
		    style: "display: none; clear: both;"
		});
		newItem.append(link);
		newItem.append(badge);
		
		newItem.appendTo($("#entityList")).show('slow');
  	}
	alert(logsToTimeline.length);
	fillTimeline(logsToTimeline);
}

function displayLog(log) {
	var contentContainer = $('#entityContent');
	contentContainer.empty();
    var logContent = $('<div class="span4" style="display: none;"><h2>' + new Date(log.start) +'</h2><p>' +  log.content + '</p></div><!--/span-->');
	logContent.appendTo(contentContainer).show('slow');
}

function filterEntity(entityName) {
	var logs = json_result[entityName];
}

function fillTimeline(logs) {
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
            var timeline = new links.Timeline(document.getElementById('mytimeline'));
            // Draw our timeline with the created data and options
            //alert("mlgb........");
            timeline.draw(logs, options);
        // });
	
}
