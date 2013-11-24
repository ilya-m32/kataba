
function temp_look(type) {
	var images = $('img.post_img');
	if (type) {
		images.mouseenter(function() {
			$(this).css('opacity','1.0');
		});
		
		images.mouseleave(function() {
			$(this).css('opacity','0');
		});
	} else
		images.unbind();
		
}
	
$(document).ready(function() {
	// Hide/show left upper menu
	$('#switch').click(function() {
		var swtch = $('#switch').html();
		if (swtch == '&lt;') {
			$('#header_content').hide();
			$('#switch').html('&gt;');
		} else {
			$('#header_content').show();
			$('#switch').html('&lt;');
		}
	});
	
	// NSFW option and it's cookies
	if ($.cookie('nsfw') == 'true') {
		$('img.post_img').css('opacity','0');
		$('#nsfw').attr('checked',true);
		temp_look(true);
	}
	
	$('#nsfw').change(function() {
		var nsfw = $('#nsfw').is(':checked');
		if (nsfw) {
			$('img.post_img').css('opacity','0');
			$.cookie('nsfw',true,{path: '/'});
			temp_look(true);
		}
		else {
			$('img.post_img').css('opacity','1.0');
			$.cookie('nsfw',false,{path: '/'});
			temp_look(false);
		}
	});
	
	// Create thread via form
	$('#send_thread').click(function() {
		$('#send_form').submit();
	});

	// Send post via ajax
	$('#send_post').click(function() {
		var csrftoken = $.cookie('csrftoken');
		var thread_id = $('#thread_id').val();
		
		var form = new FormData(document.getElementById('send_form'));
		
		$.ajax({
			type:'POST',
			crossDomain: false,
			processData: false,
			cache: false,
            contentType: false,
            MimeType: 'multipart/form-data',
			url: "/thread/"+thread_id+'/addpost',
			data: form,
			beforeSend: function(xhr) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function(output) {
				if (output.success == true) {
					$('#form_table input').val('');
					$('#refresh').click();
				}
				$('#form_table').html(output.form);
			},
		});
	});
	
	// Enabling pages
	$('#pages div').click(function() {
		document.location.href='/'+$(this).attr('data-name');
	});

	// Full image by click
	$('img.post_img').click(function() {
		var temp = '';
		temp = $(this).attr('src');
		$(this).attr('src',$(this).attr('data-alt_name'));
		$(this).attr('data-alt_name',temp);
	});
	
	// Link to post/thread
	$('span.post_link').click(function() {
		var text = $('#id_text').val();
		$('#id_text').val(text+'>>'+$(this).html().slice(1));
	});
	
	// to the start
	$('#up').click(function() {
		document.location.href = window.location.pathname+'#';
	});
	
	// Move to cloud-like 
	$('#cloud').click(function() {
		document.location.href = '/'+$('#boardname').val()+'/cloud';
	});
	
	// AJAX request for new posts in thread
	$('#refresh').click(function() {
		var csrftoken = $.cookie('csrftoken');
		var thread_id = $('#thread_id').val();
		var posts_numb = $('#post_cont div.post').length;
		$.ajax({
			type:'GET',
			crossDomain: false,
			cache: false,
			url: "/thread/update/"+thread_id+'/'+posts_numb,
			data: {},
			beforeSend: function(xhr) {
				$('#answer').html('Загружаем...');
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function(output) {
				if (output.is_new == 1) {
					$('#post_cont').html($('#post_cont').html()+output.new_threads);
					$('#answer').html('');
					
					// move to the page's end
					var url = location.href;
					location.href = "#bottom_cont";
					history.replaceState(null,null,url);
				}
				else
					$('#answer').html('Новых постов нет!');
			},
		});
	});
	
	// Show/hide post form and it's cookie
	$('#form_switch').click(function() {
		if ($.cookie('form') == 'false') {
			$.cookie('form',true,{path: '/'});
			
		}
		else {	
			$.cookie('form',false,{path: '/'});
		}
		$('#form_cont').toggle();
	});
	
	if ($.cookie('form') == 'true')
		$('#form_cont').show();

	// Show/hide options
	$('#options_button').click(function() {
		$('#options').toggle();
	});
});
