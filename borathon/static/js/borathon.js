var selected_entities = {};
var offset = 0;
EACH_LIMIT = 1000;

$(document).ready(function(){	
	if(typeof sb_url != 'undefined') {
		getAndRenderSupportBundle(sb_url, offset);
	}
});

$(document).ready(function(){
	var parts = document.URL.split("/");
	relative_url = parts[parts.length - 1];

	$(".navbar.navbar-fixed-top ul.nav li").removeClass("active");
	if(relative_url == "patterns") {
		$(".navbar .my-nav-patterns").addClass("active");
	} else if (relative_url == "") {
		$(".navbar .my-nav-home").addClass("active");
	}
// 	$(this).parent("li").addClass("active");
 	$("#entitySelectToggle").click(function() {
        var value = $(this).text();
        //alert(value);
        if(value == 'Select All') {
            $(this).text("Unselect All");
            toggleSelectAllEntities(true);
        } else {
            $(this).text("Select All");
            toggleSelectAllEntities(false);
        }
    });
});

$(".timeTravel").click(function(){
	var isNext = !$(this).hasClass('prev');
	if(isNext) {
		offset += EACH_LIMIT;
	} else {
		offset -= EACH_LIMIT;
	}
	if(offset <= 0) {
		offset = 0;
		$(".timeTravel.prev").addClass("disabled");
	} else {
		$(".timeTravel.prev").removeClass("disabled");
	}
	
    getAndRenderSupportBundle(sb_url, offset);
});


function getAndRenderSupportBundle(url, offset) {
	$("#loading").show();
	$.getJSON( "timeline", {
		url: url,
		offset: offset,
		limit: EACH_LIMIT,
	    format: "json"
	}).done(function( data ) {
		$("#loading").hide();
		renderEntityList(data);
	});
}

function generateEntitiesGroup(itemName) {
	var panel = $("<div />", {
	    "class": "panel panel-default"
	});
	var panel_title = $("<a />", {
	    href: "#collapse_" + itemName,
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
	panel.append($('<div id="collapse_' + itemName +'" class="panel-collapse collapse in" ><div class="panel-body"><div class="sidebar-nav"><ul class="nav nav-list entityList"></ul></div></div></div>'));
	return panel;
}

function generateListedItem(itemName, logs) {
	var link = $("<a />", {
	    href: "#",
	    "class": "entity-link selected", // you need to quote "class" since it's a reserved keyword
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
	$("#accordion").empty();
	var total_logs = [];
	for(var entityType in data) {
		entity_logs_count = 0;
		entities = data[entityType];
		entityGroup = generateEntitiesGroup(entityType);
        
		
		for(var entityName in entities) {
			logs = entities[entityName];
			selected_entities[entityName] = logs;
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

function toggleSelectAllEntities(isToSelect) {
   $(".entity-link").each(function() {
	  var entityName = $(this).data("name");
	  var logs = $(this).data("logs");
      if(isToSelect) {
        $(this).addClass('selected');
		selected_entities[entityName] = logs;
      } else {
        $(this).removeClass('selected');
		delete selected_entities[entityName];
      }
   });
   var result = [];
   for(var e in selected_entities) {
       result = result.concat(selected_entities[e]);
   }
   fillTimeline(result, "logsTimeline");
}
