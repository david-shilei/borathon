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

var selected_entities = []

$(document).ready(function(){	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
  	buildForEntities(json_result);
});

function buildForEntities(entities) {
	$("#entityList").empty();
	
	var logsToTimeline = [];
  	for(var entityName in entities) {
		var logs = entities[entityName];
		logsToTimeline.push(logs);
		var link = $("<a />", {
		    href: "#",
		    "class": "entity-link", // you need to quote "class" since it's a reserved keyword
		    text: entityName,
			title: entityName,
			style: "clear:both;"
		});
		link.data("name", entityName);
		link.data("logs", logs);
		
	  	link.click(function(){
			logs = filterLogs($(this));
			fillTimeline(logs);
	  	});
		
		var badge = $("<span />", {
			"class": "badge",
			text: logs.length,
			style: "float:right"
		});

		var newItem = $("<li />", {
		    style: "display: none;"
		});
		link.append(badge);
		newItem.append(link);
		
		newItem.appendTo($("#entityList")).show('slow');
  	}

	fillTimeline(logsToTimeline);
}

function displayLog(log) {
	var contentContainer = $('#entityContent');
	contentContainer.empty();
    var logContent = $('<div class="span4" style="display: none;"><h2>' + new Date(log.start) +'</h2><p>' +  log.content + '</p></div><!--/span-->');
	logContent.appendTo(contentContainer).show('slow');
}

function filterLogs(entityLink) {
	var entityName = entityLink.data("name");
	var selected = entityLink.hasClass('selected');

	if(selected) {
		entityLink.removeClass('selected');
		while (selected_entities.indexOf(entityName) !== -1) {
		  selected_entities.splice(selected_entities.indexOf(entityName), 1);
		}
	} else {
		entityLink.addClass('selected');
		selected_entities.push(entityName);
	}

	var logs = [];
	for(var i in selected_entities) {
		var e = selected_entities[i];
		logs.push(json_result[e]);
	}
	
	return logs;
}


