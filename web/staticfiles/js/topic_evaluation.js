var evaluations_dict = null;

function run_topics_eval(topic_modelling, csrf_token, criterions) {
    // Get initial existing evaluations
    $.ajax(
        {
            url: '/api/criterion_eval/?topic_modelling=' + topic_modelling,
            method: 'GET',
            success: function (result) {
                if (result.status !== 200) {
                    alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                    return;
                }
                evaluations_dict = result.criterions;
            }
        }
    );

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
        var topic_id = $('#criterionTopicID').val();

        if(!criterion.is_categorical){
            $('#criterionIsCategorical').val(0);
            if(criterion.is_integer){
                step = 1;
            } else {
                step = 0.1;
            }
            control_html = "<input type='range' id='evalValue' min='" + criterion.value_range_from.toString() +
                                    "' max='" + criterion.value_range_to.toString() + "' step='" + step.toString() + "' class='custom-range'>";
            $('#evalValueWrapper').html("<span id='evalTooltip'>55</span>");
            $('#evalControl').html(control_html);
            var searchInput = document.querySelector('#evalValue');
            searchInput.addEventListener('input', function() {$('#evalTooltip').html($('#evalValue').val());});
            $('#evalControl').removeClass('col-md-12').addClass('col-md-11');
            $('#evalValueWrapper').addClass('col-md-1').removeClass('hide');
            try {
                $('#evalValue').val(evaluations_dict[$('#criterionSelect').val()][topic_id]);
            } catch (e) {
            }
            $('#evalTooltip').html($('#evalValue').val());
        } else {
            $('#criterionIsCategorical').val(1);
            control_html = '<select class="form-control select2bs4" id="evalValue" style="width: 100%;">';
            for (key in criterion.cat_values) {
                control_html += '<option value="' + key.toString() + '">' + criterion.cat_values[key].char_value + '</option>'
            }
            control_html += '</select>';
            $('#evalTooltip').html("");
            $('#evalControl').html(control_html);
            try {
                $('#evalValue').val(evaluations_dict[$('#criterionSelect').val()][topic_id].toString());
            } catch (e) {
            }
            $('#evalValue').select2({
              theme: 'bootstrap4'
            });
            $('#evalControl').removeClass('col-md-11').addClass('col-md-12');
            $('#evalValueWrapper').addClass('hide');
        }
    }

    // Event management, init
    create_eval_control();
    $('#criterionSelect').change(create_eval_control);
    $('.set-topic-eval').click(function(e) {
        e.preventDefault();
        var topic_id = e.target.id.split("evalTopic_")[1];

        try {
            if ($('#criterionIsCategorical').val() == 1) {
                $('#evalValue').val(evaluations_dict[$('#criterionSelect').val()][topic_id].toString());
                $('#evalValue').select2({
                    theme: 'bootstrap4'
                });
            } else {
                $('#evalValue').val(evaluations_dict[$('#criterionSelect').val()][topic_id]);
                $('#evalTooltip').html($('#evalValue').val());
            }
        } catch (e) {
        }

        $('#topicEvalModal').modal();
        $('#criterionTopicID').val(topic_id);
    });

    $('#evalSave').click(function(){
        $.ajax(
            {
                url: '/api/criterion_eval/',
                method: 'POST',
                data: {
                    "topic_modelling": topic_modelling,
                    "topic_id": $('#criterionTopicID').val(),
                    "criterion_id": $('#criterionSelect').val(),
                    "value": $('#evalValue').val(),
                },
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrf_token);
                },
                success: function (result) {
                    if (result.status === 500) {
                        alert(result.error);
                        return;
                    } else if (result.status !== 200) {
                        alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу или " +
                            "обратитесь к Администратору системы");
                        return;
                    }
                    if(!parseInt(result.criterion_id) in evaluations_dict) {
                        evaluations_dict[parseInt(result.criterion_id)] = {};
                    }
                    evaluations_dict[parseInt(result.criterion_id)][result.topic_id] = result.value;
                }
            }
        );
    });
}
