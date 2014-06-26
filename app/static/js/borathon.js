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


var pr_result = [
	{
		"id": 1266492, 
		"summary": "Nimbus RbVmomi refactor sub-task: VM clone related methods"
	},
	{
		"id": 1198908, 
		"summary": "Timeout when fetching esx support bundle"
	}
]

var selected_entities = {};

$(document).ready(function(){	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
	// renderEntityList(json_result);
  	// buildForEntities(json_result);
	getAndRenderSupportBundle(sb_url);
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

function getAndRenderSupportBundle(url) {
	$.getJSON( "timeline", {
		url: url,
	    format: "json"
	}).done(function( data ) {
		renderEntityList(data);
	});
}

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
		
		// TODO
		displayPRs(pr_result);
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

function displayPRs(prs) {
	for(i = 0; i < prs.length; i++) {
		pr = prs[i];
		var url = "https://bugzilla.eng.vmware.com/show_bug.cgi?id=" + pr.id;

		var pr_link = $("<a />", {
		    href: url,
		    text: "PR#" + pr.id + ": " + pr.summary
		});

		$("#prsContainer").append($('<p />').append(pr_link));
	}
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
