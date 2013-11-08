
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
	
	if ($.cookie('nsfw') == 'true') {
		$('img.post_img').css('opacity','0');
		$('#nsfw').attr('checked',true);
		temp_look(true);
	}
	
	$('#nsfw').change(function() {
		var nsfw = $('#nsfw').is(':checked');
		if (nsfw) {
			$('img.post_img').css('opacity','0');
			$.cookie('nsfw',true);
			temp_look(true);
		}
		else {
			$('img.post_img').css('opacity','1.0');
			$.cookie('nsfw',false);
			temp_look(false);
		}
	});
	
	$('#send').click(function() {
		$('#send_form').submit();
	});
	
	$('#pages div').click(function() {
		document.location.href='/'+$(this).attr('name');
	});

	$('img.post_img').click(function() {
		var temp = '';
		temp = $(this).attr('src');
		$(this).attr('src',$(this).attr('data-alt_name'));
		$(this).attr('data-alt_name',temp);
	});
	
	$('span.post_link').click(function() {
		var text = $('#id_text').val();
		$('#id_text').val(text+'>>'+$(this).html().slice(1)) 
	});
	
	$('#up').click(function() {
		document.location.href= window.location.pathname+'#'
	});
	
	$('#refresh').click(function() {
		var csrftoken = $.cookie('csrftoken');
		var thread_id = $('#thread_id').val();
		var posts_numb = $('#post_cont div.post').length;
		$.ajax({
			type:'POST',
			settings: {
				crossDomain: false,
			},
			url: "/thread/update",
			data: {'posts_numb':posts_numb, 'thread_id':thread_id},
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
	
	$('#form_switch').click(function() {
		$('#form_cont').toggle();
	});
	
});
