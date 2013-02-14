$(function () {
	'use strict';
	var is_canceled=false;
	var is_paused=false;
	var data_resume = null;
	var chunked_uploads_jqXHR = null;
	$('#start_upload').attr('disabled', true);
	$('#pause_upload').attr('disabled', true);
	$('#resume_upload').attr('disabled', true);
	$('#cancel_upload').attr('disabled', true);
	
	//authentication send in the header, to log with ApiKey
	var authentication = {
			username: chunked_uploads_endpoints.username,
			api_key: chunked_uploads_endpoints.api_key
	}
	
	$('#fileupload').fileupload({        
        url: chunked_uploads_endpoints.upload_url,
	   	dataType: 'json',
	   	maxChunkSize: 1048576,
	    singleFileUploads: false,
	   	maxNumberOfFiles: 1,
	    multipart: false,
	    xhrFields: {
	        withCredentials: true
	    },
	    headers: authentication,
	    add: function (e, data) {
	    	//Get json from server to know if and upload has already been started
	    	$.ajax({
	    		type: "GET",
	    		dataType: "json",
	    		data: authentication,
	    		url: chunked_uploads_endpoints.upload_url,
	    		xhrFields: {withCredentials: true},
	    		success: function(current_upload){
	    			//If not null then an upload has already been started
	    			if (current_upload != ""){
	    				//checks if the file selected match with the file currently uploaded on the server 
	    				if (data.files[0].size == current_upload[0].total_size){
	    					//the file match, so we'll resume the upload from uploadedBytes
	    					data.uploadedBytes = current_upload[0].size;
	    				}
	    				else{
	    					//The file doesn't match, so delete the current upload on the server
	    					$.ajax({
			    	    		type: current_upload[0].delete_type,
			    	    		url: current_upload[0].delete_url,
			    	    		data: authentication,
			    		  });
	    				}
	    			}
	    		},
	    	});
	    	
	    	$('#start_upload').attr('disabled', false);
	    	$('#start_upload').one('click', function (e) {
	            e.preventDefault();
	            chunked_uploads_jqXHR = data.submit();
	        });
	    },
	    start: function (e, data){
	    	if (typeof chunked_uploads_start === "function") {
	    		chunked_uploads_start();
			}
	    },
	    done: function (e, data) {
	        $('#start_upload').hide();
    		$('#pause_upload').hide();
    		$('#resume_upload').hide();
    		$('#cancel_upload').hide();
    		
	    	chunked_uploads_endpoints.done_url = chunked_uploads_endpoints.done_url.replace('00000000-0000-0000-0000-000000000000', data.result[0].upload_uuid);
	    	//send COMPLETE request
	    	$.ajax({
	    		type: "POST",
	    		dataType: "json",
	    		headers: authentication,
	    		url: chunked_uploads_endpoints.done_url,
	    		xhrFields: {withCredentials: true},
	    		success: function(current_upload){
	    			//error callback if upload state is FAIL
	    			if (current_upload[0].state=="FAIL"){
	    				if (typeof chunked_uploads_error === "function") {
	    					chunked_uploads_error();
		    			}
	    			}
	    			//complete and video_url callback if success
	    			else{
	    				if (typeof chunked_uploads_complete === "function") {
	    					chunked_uploads_complete();
		    			}
	    				if (typeof chunked_uploads_video_url === "function") {
		    				chunked_uploads_video_url(current_upload[0].video_url);
		    			}
	    			}
	    		},
	    		error: function(){
	    			if (typeof chunked_uploads_error === "function") {
    					chunked_uploads_error();
	    			}
	    		}
			});    		
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
	    },
    });
	   
    $('#cancel_upload').click(function (e) {
    	if (!is_paused){
    		//if cancel is clicked during the upload
			is_canceled = true;
			//stop the download
			chunked_uploads_jqXHR.abort();
			//wait 1s before sending a DELETE request to the server
			setTimeout(function() {
				$.ajax({
					  dataType: "json",
					  url: chunked_uploads_endpoints.upload_url,
					  data: authentication,
					  xhrFields: {withCredentials: true},
					  success: function(current_upload){
						  $.ajax({
			    	    		type: current_upload[0].delete_type,
			    	    		url: current_upload[0].delete_url,
			    	    		headers: authentication,
			    		  });
					  }
				});
			},1000);
		}
		else{
			//if cancel is clicked while pause we send the DELETE request
			$.ajax({
				  dataType: "json",
				  url: chunked_uploads_endpoints.upload_url,
				  xhrFields: {withCredentials: true},
				  data: authentication,
				  success: function(current_upload){
					  $.ajax({
		    	    		type: current_upload[0].delete_type,
		    	    		url: current_upload[0].delete_url,
		    	    		headers: authentication,
		    		  });
				  }
			});
		}
    	$('#pause_upload').attr('disabled', true);
		$('#resume_upload').attr('disabled', true);
		$('#cancel_upload').attr('disabled', true);
		$('.progress').css(
	            'width',
	            0 + '%'
	    );
		if (typeof chunked_uploads_error === "function") {
			chunked_uploads_error();
		}
	});
	
	$('#pause_upload').click(function (e) {
		is_paused = true;
		chunked_uploads_jqXHR.abort();
		if (typeof chunked_uploads_stop === "function") {
			chunked_uploads_stop();
		}		
		$('#pause_upload').attr('disabled', true);
		$('#resume_upload').attr('disabled', false);
	});
	
	$('#resume_upload').click(function (e) {
		is_paused = false;
		$.ajax({
			  dataType: "json",
			  url: chunked_uploads_endpoints.upload_url,
			  data: authentication,
			  xhrFields: {withCredentials: true},
			  success: function(current_upload){
				  data_resume.uploadedBytes = current_upload[0].size;
				  chunked_uploads_jqXHR = data_resume.submit();
			  }
		});
		if (typeof chunked_uploads_start === "function") {
    		chunked_uploads_start();
		}
		$('#resume_upload').attr('disabled', true);
		$('#pause_upload').attr('disabled', false);
	});
	
	//connection listener
	if ('onLine' in navigator) {
        //event listener on connection found
		window.addEventListener('online', function(){
    		is_paused = false;
    		$.ajax({
    			  dataType: "json",
    			  url: chunked_uploads_endpoints.upload_url,
    			  data: authentication,
    			  xhrFields: {withCredentials: true},
    			  success: function(current_upload){
    				  data_resume.uploadedBytes = current_upload[0].size;
    				  chunked_uploads_jqXHR = data_resume.submit();
    			  }
    		});
    		if (typeof chunked_uploads_start === "function") {
	    		chunked_uploads_start();
			}
    		$('#resume_upload').attr('disabled', true);
    		$('#pause_upload').attr('disabled', false);
        });
        
		//event listener on connection lost
        window.addEventListener('offline', function(){
        	if (chunked_uploads_jqXHR != null){
	    		is_paused = true;
	    		$('#pause_upload').attr('disabled', true);
	    		$('#resume_upload').attr('disabled', true);
	    		chunked_uploads_jqXHR.abort();
        	}
        });
    };
});