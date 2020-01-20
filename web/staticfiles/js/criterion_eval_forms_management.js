$('.collapse').collapse('hide');
$('h3').hover(
    function () {
        $(this).find('i').addClass('fas');
        $(this).find('i').removeClass('far');
    },
    function () {
        $(this).find('i').addClass('far');
        $(this).find('i').removeClass('fas');
    }
);

$('h3').click(function () {
    if ($(this).find('i').hasClass('fa-caret-square-down')) {
        $(this).find('i').addClass('fa-caret-square-up');
        $(this).find('i').removeClass('fa-caret-square-down');
    } else {
        $(this).find('i').addClass('fa-caret-square-down');
        $(this).find('i').removeClass('fa-caret-square-up');
    }
});

$('#topic_modelling').change(function () {
    // Disable stuff
    $('button[type=submit]').attr('disabled', 'disabled');
    $('#criterions').html("");
    $('#criterions').select2({
        closeOnSelect: true,
    });
    $('#criterion_q').html("");
    $('#criterion_q').select2({
        closeOnSelect: true,
    });

    $('#group').html("");
    $('#group').select2({
        closeOnSelect: true,
    });

    $.ajax(
        {
            url: '/api/criterion_eval_util/?topic_modelling=' + $('#topic_modelling').val(),
            method: 'GET',
            success: function (result) {
                if (result.status !== 200) {
                    alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                    return;
                }

                // Handle criterions
                var criterions_list_html = "";
                let mark_selected = true;
                for (let criterion of result.criterions) {
                    if (mark_selected) {
                        criterions_list_html += '<option selected value="' + criterion.id + '">' + criterion.name + '</option>';
                        mark_selected = false;
                    } else {
                        criterions_list_html += '<option value="' + criterion.id + '">' + criterion.name + '</option>';
                    }
                }
                $('#criterions').html(criterions_list_html);
                $('#criterions').select2({
                    closeOnSelect: true,
                });

                $('#collapseAnalyticalQuerySetting').collapse('show');
                $('#criterion_q').html(criterions_list_html);
                $('#criterion_q').select2({
                    closeOnSelect: true,
                });

                // Handle groups
                var groups_list_html = "<option selected value='-1'>-----Мои группы-----</option>";
                for (let group of result.my_groups) {
                    groups_list_html += "<option value='" + group.id + "'>" + group.name + "</option>";
                }
                groups_list_html += "<option value='-2'>-----Публичные группы-----</option>";
                for (let group of result.public_groups) {
                    groups_list_html += "<option value='" + group.id + "'>" + group.name + "</option>";
                }
                $('#collapseFilteringSetting').collapse('show');
                $('#group').html(groups_list_html);
                $('#group').select2({
                    closeOnSelect: true,
                });

                // Reenable stuff
                $('button[type=submit]').removeAttr('disabled');
            },
            error: function (result) {
                alert("Возможно отсутствует соединение с интернетом. Если проблема повторяется, обратитесь к администратору системы");
            }
        }
    );
});
