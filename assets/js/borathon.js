$(document).ready(function(){
	var data = [{"content":"RecordOp ASSIGN: guest, 53. Sent notification immediately.","loglevel":"verbose","start":1399706542422},{"content":"RecordOp ASSIGN: summary.guest, 17. Sent notification immediately.","loglevel":"verbose","start":1399706546913},{"content":"Done Dispatching Vigor callback","loglevel":"verbose","start":1399706556078}]
	
	// $.get( "http://ec2-54-254-246-134.ap-southeast-1.compute.amazonaws.com/borathon/hostd.log.json", function( data, status) {
	//
	// });
	//
	data = data.slice(0, 5)
  	$.each(data,function(idx,item){
		time = new Date(item.start);
		var newItem = $('<li style="display: none;"><a class="entity-link" href="#" >' + item.content  + '</a></li>');
		var link = newItem.children(".entity-link")
		link.data("time", time);
		link.data("content", item.content);
		link.data("loglevel", item.loglevel);
		newItem.appendTo($("#entityList")).show('slow');
  	});
	  
	  
  	$(".entity-link").click(function(){
  		var contentContainer = $('#entityContent');
  		contentContainer.empty();
          var content = $('<div class="span4" style="display: none;"><h2>' + $(this).data("content") +'</h2><p>' + $(this).data("time")  + '</p></div><!--/span-->');
    	  content.appendTo(contentContainer).show('slow');
  	});
});