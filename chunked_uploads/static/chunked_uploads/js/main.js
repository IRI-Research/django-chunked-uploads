$(function () {
	'use strict';
	var is_canceled=false;
	var is_paused=false;
	var jqXHR = null;
	var data_resume = null;
	$('#start_upload').attr('disabled', true);
	$('#pause_upload').attr('disabled', true);
	$('#resume_upload').attr('disabled', true);
	$('#cancel_upload').attr('disabled', true);
	
	$('#fileupload').fileupload({        
        url: chunked_uploads_endpoints.upload_url,
	   	dataType: 'json',
	   	acceptFileTypes: /(\.|\/)(avi|mpe?g|wmv)$/i,
	   	maxChunkSize: 1048576,
	   	maxNumberOfFiles: 1,
	    multipart: false,
	    autoUpload: false,
	    add: function (e, data) {
	    	$('#start_upload').attr('disabled', false);
	    	
	    	$('#start_upload').one('click', function (e) {
	            e.preventDefault();
	            jqXHR = data.submit();
	        });
	    },
	    done: function (e, data) {
	    	chunked_uploads_endpoints.done_url = chunked_uploads_endpoints.done_url.replace('00000000-0000-0000-0000-000000000000', data.result[0].upload_uuid);
	    	$.get(chunked_uploads_endpoints.done_url, "json");
	        $.each(data.result, function (index, file) {
                $('<p/>').text(file.name).appendTo(document.body);
            });
	        $('#start_upload').hide();
    		$('#pause_upload').hide();
    		$('#resume_upload').hide();
    		$('#cancel_upload').hide();
	    },
	    progressall: function (e, data) {
	    	var progress = parseInt(data.loaded / data.total * 100, 10);
	        $('.progress').css(
	            'width',
	            progress + '%'
	        );
    	},
	    send: function(e, data) {
	    	$("#fileupload").hide();
	    	$('#start_upload').hide();
            $('#pause_upload').attr('disabled', false);
        	$('#cancel_upload').attr('disabled', false);
	    },
	    fail: function(e, data) {
	    	data_resume = data;
	    }
    });
	   
    $('#cancel_upload').click(function (e) {
		if (!is_paused){
			is_canceled = true;
			jqXHR.abort();
	    	$('#pause_upload').attr('disabled', true);
			$('#resume_upload').attr('disabled', true);
			setTimeout(function() {
				$.getJSON(chunked_uploads_endpoints.upload_url, function(current_upload) {	
	    			$.ajax({
	    	    		type: current_upload[0].delete_type,
	    	    		url: "http://localhost/" + current_upload[0].delete_url
	    		    });
	        	});
			},1000);
		}
		else{
			$.getJSON(chunked_uploads_endpoints.upload_url, function(current_upload) {	
    			$.ajax({
    	    		type: current_upload[0].delete_type,
    	    		url: "http://localhost/" + current_upload[0].delete_url
    		    });
        	});
		}
	});
	
	$('#pause_upload').click(function (e) {
		is_paused = true;
		jqXHR.abort();
		$('#pause_upload').attr('disabled', true);
		$('#resume_upload').attr('disabled', false);
	});
	
	$('#resume_upload').click(function (e) {
		is_paused = false;
        $.getJSON(chunked_uploads_endpoints.upload_url, function (current_upload) {
        	data_resume.uploadedBytes = current_upload[0].size;
        	jqXHR = data_resume.submit();
        });
		$('#resume_upload').attr('disabled', true);
		$('#pause_upload').attr('disabled', false);
	});
	
	$('#clean_upload').click(function (e) {
		$.getJSON(chunked_uploads_endpoints.upload_url, function(current_upload) {	
			$.ajax({
	    		type: current_upload[0].delete_type,
	    		url: current_upload[0].delete_url
		    });
    	});
	});
});