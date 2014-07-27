// simple tags jquery code for ajax tag complete

function get_last_tag(tags) {
    tag = '';
    tags = tags.split(',');
    if (tags.length)
        tag = $.trim(tags[tags.length-1]);
    return tag;
}

function complete_tag(tag) {
    var tag_field = $('#id_tagcomplete');
    var csrftoken = $.cookie('csrftoken');
    var limit = 7;
    var tags = [];

    $.ajax({
        type:'GET',
        crossDomain: false,
        processData: false,
        cache: false,
        url: encodeURI("/tags/complete/"+tag+'/'+limit),
        data: {},
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function(output) {
            if (output.length) {
                var html = '';
                tag_field.show();

                output.forEach(function(e) {
                    html += '<div>'+e+'</div>';
                });

                tag_field.html(html);
            } else 
                tag_field.hide();
        },
    });
}



$(document).ready(function() {
	// Tag autocomplete
    $('#id_tags').keyup(function(e) {
        var last_tag = get_last_tag($(this).val());
        if (last_tag.length)
            complete_tag(last_tag);
        else
            $('#id_tagcomplete').hide();
    });


    $('body').on("click", "#id_tagcomplete div", function() {
        var field = $('#id_tags');
        var tag = $(this).html();
        var last_tag = get_last_tag(field.val());
        if (last_tag) {
            field.val(field.val()+tag.slice(last_tag.length)+', ');
            $(this).parent().hide();
            field.focus();
        }
    });
});