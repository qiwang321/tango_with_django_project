$(document).ready(function() {

    // the "like" button
    $('#likes').click(function(){
	var catid;
	catid = $(this).attr("data-catid");
	// the third parameter is the callback parameter
	$.get('/rango/like_category/', {category_id: catid}, function(data){
	    $('#like_count').html(data);
	    $('#likes').hide();

	}); 
    });
    
    // the real-time suggestion
    $('#suggestion').keyup(function(){
	var query;
	query = $(this).val();
	$('#cats').html("none");
	$.get('/rango/suggest_category/', {suggestion: query}, function(data){
	    $('#cats').html(data);
	});
    });
    
    // quick add page
    $('.quick_add').click(function() {
	var catid;
	catid = $(this).attr("data-catid");
	title = $(this).attr("data-title");
	url = $(this).attr("data-url");
	$.get('/rango/auto_add_page/', {category_id: catid, url: url, title: title}, function(data) {
	    $('#page_list').html(data);
	    $(this).hide();
	});
    });
})


