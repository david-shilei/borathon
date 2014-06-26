// // var myObject = eval('(' + myJSONtext + ')');
// // var myJSONText = JSON.stringify(myObject, replacer);
// // function replacer(key, value) {
// //     if (typeof value === 'number' && !isFinite(value)) {
// //         return String(value);
// //     }
// //     return value;
// // }

// var myObject = eval('(' + myJSONtext + ')');
// var myJSONText = JSON.stringify(myObject, replacer);
// function replacer(key, value) {
//     if (typeof value === 'number' && !isFinite(value)) {
//         return String(value);
//     }
//     return value;
// }

var json_result = {
	"host": {
		"host-9:91:76e1b7f8-0-13e9": [
			{
				"start": 1231231231123,
				"line": 234,
				"file": "hostd.log",
				"className": "host",
				"content": "Failed to load virtual machine: vim.fault.FileNotFound",
 			    "detail":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound." }],
		"host-9:94:22480d43-0-1ae8": [
			{
				"start": 1231231231231,
				"line": 235,
				"file": "hostd.log",
				"className": "host",
				"content": "Failed to load virtual machine: vim.fault.FileNotFound",
				"detail": "2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound." }]
	},
	"vm": {
		"vm-esx.0": [
		{
			"start": 1231231231123,
			"line": 234,
			"file": "hostd.log",
			"className": "host",
			"content": "Failed to load virtual machine: vim.fault.FileNotFound",
		    "detail":"2014-05-09T23:31:24.304Z [321C2B70 info 'Vmsvc.vm:/vmfs/volumes/vsan:52a7980961ea0ddf-e8c7fef416d27ea0/484c6d53-e861-52ac-6e8c-2c44fd7c2d24/io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx' opID=host-9:91:76e1b7f8-0-13e9 user=vpxuser] Failed to load virtual machine: vim.fault.FileNotFound."
		}]
	}
}

var selected_entities = {};

$(document).ready(function(){	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
	renderEntityList(json_result);
  	// buildForEntities(json_result);
});


// <div class="panel panel-default">
//   <div class="panel-heading">
//     <h4 class="panel-title">
//       <a data-toggle="collapse" data-parent="#accordion" href="#collapseOne">
//         Collapsible Group Item #1
//       </a>
//     </h4>
//   </div>
//   <div id="collapseOne" class="panel-collapse collapse in">
//     <div class="panel-body">
//       VSDSD
//     </div>
//   </div>
// </div>

function generateEntitiesGroup(itemName) {
	var panel = $("<div />", {
	    "class": "panel panel-default"
	});
	var panel_title = $("<a />", {
	    href: "#collapseOne",
		"class": "entity-type-title",
		"data-toggle": "collapse",
		"data-parent": "#accordion",
	    text: itemName
	}); 
	var panel_body = $("<div />", {
	    "class": "panel-body"
	});

	panel.append($('<div class="panel-heading" />').append($('<h4 class="panel-title" />').append(panel_title)));
	// panel.append(panel_collapse);
	panel.append($('<div id="collapseOne" class="panel-collapse collapse in" ><div class="panel-body"><div class="sidebar-nav"><ul class="nav nav-list entityList"></ul></div></div></div>'));
	return panel;
}

function generateListedItem(itemName, logs) {
	var link = $("<a />", {
	    href: "#",
	    "class": "entity-link", // you need to quote "class" since it's a reserved keyword
	    text: itemName,
		title: itemName,
		style: "clear:both;"
	});
	link.data("name", itemName);
	link.data("logs", logs);
	
  	link.click(function(){
		logs = filterLogs($(this));
		fillTimeline(logs, "logsTimeline");
  	});
	
	var badge = $("<span />", {
		"class": "badge",
		text: logs.length,
		style: "float:right"
	});

	var newItem = $("<li />", {
	    // style: "display: none;"
	});
	link.append(badge);
	newItem.append(link);
	
	return newItem;
}

function renderEntityList(data) {
	total_logs = [];
	for(var entityType in data) {
		entity_logs_count = 0;
		entities = data[entityType];
		entityGroup = generateEntitiesGroup(entityType);
		
		for(var entityName in entities) {
			logs = entities[entityName];
			entity_logs_count += logs.length
			total_logs = total_logs.concat(logs);
			// total_logs += logs;
			var new_item = generateListedItem(entityName, logs);
			entityGroup.find(".entityList").append(new_item);
		}
		
		var entityTypeTitle = entityGroup.find(".entity-type-title");
		entityTypeTitle.text(entityTypeTitle.text() + "(" + entity_logs_count + ")");
		$("#accordion").append(entityGroup);
	}

	fillTimeline(total_logs, "logsTimeline");
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
	var logs = entityLink.data("logs");

	if(selected) {
		entityLink.removeClass('selected');
		delete selected_entities[entityName];
		// while (selected_entities.indexOf(entityName) !== -1) {
// 		  selected_entities.splice(selected_entities.indexOf(entityName), 1);
// 		}
	} else {
		entityLink.addClass('selected');
		selected_entities[entityName] = logs;
	}

	var result = [];
	for(var e in selected_entities) {
		result = result.concat(selected_entities[e]);
	}

	return result;
}
