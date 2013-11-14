
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
		var form_data = $('#send_form').serializeArray();
		$.ajax({
			type:'POST',
			settings: {
				crossDomain: false,
			},
			url: "/thread/"+thread_id+'/addpost',
			data: {'data':form_data,'test':'test'},
			beforeSend: function(xhr) {
				$('#answer').html('Загружаем...');
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function(output) {
				if (output.is_new == 1) {
					$('#post_cont').html($('#post_cont').html()+output.new_threads);
					$('#answer').html('');
				}
				else
					$('#answer').html('Новых постов нет!');
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
		$('#id_text').val(text+'>>'+$(this).html().slice(1)) 
	});
	
	// to the start
	$('#up').click(function() {
		document.location.href= window.location.pathname+'#'
	});
	
	// AJAX request for new posts in thread
	$('#refresh').click(function() {
		var csrftoken = $.cookie('csrftoken');
		var thread_id = $('#thread_id').val();
		var posts_numb = $('#post_cont div.post').length;
		$.ajax({
			type:'GET',
			settings: {
				crossDomain: false,
				cache: false,
			},
			url: "/thread/update/"+thread_id+'/'+posts_numb,
			data: {},
			beforeSend: function(xhr) {
				$('#answer').html('<progress max="25">Загружаем</progress>');
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function(output) {
				if (output.is_new == 1) {
					$('#post_cont').html($('#post_cont').html()+output.new_threads);
					$('#answer').html('');
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

	// Image validation
	$(':file').change(function(){
		var file = this.files[0];
		size = file.size;
		type = file.type;

		// I'll write it later
	});
});
