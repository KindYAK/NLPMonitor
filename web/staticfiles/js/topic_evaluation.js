function run_topics_eval(csrf_token, criterions) {
    // Initialize criterions select
    var criterions_options = "";
    for (var key in criterions){
        criterion = criterions[key];
        criterions_options += "<option value='" + criterion.id + "'>" + criterion.name + "</option>"
    }
    $('#criterionSelect').html(criterions_options);
    $('.select2bs4').select2({
      theme: 'bootstrap4'
    });

    // Create eval control
    function create_eval_control(){
        var criterion = criterions[$('#criterionSelect').val()];

        if(!criterion.is_categorical){
            if(criterion.is_integer){
                step = 1;
            } else {
                step = 0.1;
            }
            control_html = "<input type='range' id='evalValue' min='" + criterion.value_range_from.toString() +
                                    "' max='" + criterion.value_range_to.toString() + "' step='" + step.toString() + "' class='custom-range'>";
            $('#evalValueWrapper').html("<span id='evalTooltip'>55</span>");
            $('#evalControl').html(control_html);
            $('#evalTooltip').html($('#evalValue').val());
            var searchInput = document.querySelector('#evalValue');
            searchInput.addEventListener('input', function() {$('#evalTooltip').html($('#evalValue').val());});
            $('#evalControl').removeClass('col-md-12').addClass('col-md-11');
            $('#evalValueWrapper').addClass('col-md-1').removeClass('hide');
        } else {
            control_html = '<select class="form-control select2bs4" id="evalValue" style="width: 100%;">';
            for (key in criterion.cat_values) {
                control_html += '<option value="' + key.toString() + '">' + criterion.cat_values[key].char_value + '</option>'
            }
            control_html += '</select>';
            $('#evalTooltip').html("");
            $('#evalControl').html(control_html);
            $('#evalValue').select2({
              theme: 'bootstrap4'
            });
            $('#evalControl').removeClass('col-md-11').addClass('col-md-12');
            $('#evalValueWrapper').addClass('hide')
        }
    }

    // Event management, init
    create_eval_control();
    $('#criterionSelect').change(create_eval_control);
    $('.set-topic-eval').click(function(e) {
        e.preventDefault();
        $('#topicEvalModal').modal();
    });
}
