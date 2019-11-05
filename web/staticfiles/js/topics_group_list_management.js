var topic_groups_list = null;

function initialize_groups_select(){
    var options = "<option selected value='-1'>-----Группа топиков...-----</option>";
    for (group of topic_groups_list.my_groups){
        options += "<option value='" + group.name + "'>" + group.name + "</option>"
    }
    options += "<option value='-1'>-----Публичные группы-----</option>";
    for (group of topic_groups_list.public_groups){
        options += "<option value='" + group.name + "'>" + group.name + "</option>"
    }
    $('#topicFilterInput').html(options);
}

function run_group_list_management(topic_modelling, csrf_token){
    $.ajax(
        {
            url: '/api/topic_group/?topic_modelling=' + topic_modelling,
            method: 'GET',
            success: function (result) {
                if (result.status !== 200) {
                    alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                    return;
                }
                topic_groups_list = result;
                initialize_groups_select();
            }
        }
    );

    function generate_topic_group_list(topic_groups, prefix, topic_id) {
        list_html = "<ul class=group-list>";
        for (topic_group of topic_groups) {
            is_checked = false;
            for (topic of topic_group.topics) {
                if (topic_id === topic.topic_id) {
                    is_checked = true;
                    break;
                }
            }
            list_html += "<li>";
            list_html += '<div class="icheck-primary d-inline">\n' +
                '           <input type="checkbox" topic_id="' + topic_id + '" class="group-check-' + prefix + '" id="groupCheck_' + prefix + '_' + topic_group.id + '"' +
                '                                                    ' + (is_checked ? 'checked="checked"' : '') + '" ' +
                '                                                    ' + (prefix === 'public' ? 'disabled' : '') + '>\n' +
                '           <label for="groupCheck_' + prefix + '_' + topic_group.id + '"></label>\n' +
                '         </div>';
            list_html += " " + topic_group.name + '(' + topic_group.topics.length + ' топиков)';
            list_html += (prefix === "my" ? '<i class="fas fa-times remove-topic" id="removeTopic_' + topic_group.id + '" data-toggle="tooltip" data-placement="top" title="Удалить группу топиков"></i>' : '');
            list_html += "</li>";
        }
        list_html += "</ul>";
        return list_html;
    }

    function manage_topics_onclick(topic_id){
        $('#addGroup').attr('topic_id', topic_id);

        $('#myTopicGroupsList').html(generate_topic_group_list(topic_groups_list.my_groups, "my", topic_id));
        $('.group-check-my').click(function (e) {
            $.ajax(
                {
                    url: '/api/topic_group/' + e.target.id.split("groupCheck_my_")[1] + '/',
                    method: 'PATCH',
                    data: {
                        "topic_id": e.target.attributes['topic_id'].value,
                        "is_checked": e.target.checked,
                    },
                    beforeSend: function (request) {
                        request.setRequestHeader("X-CSRFToken", csrf_token);
                    },
                    success: function (result) {
                        if (result.status !== 200) {
                            alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу или " +
                                "обратитесь к Администратору системы");
                            return;
                        }
                        for (topic_group of topic_groups_list.my_groups) {
                            if (topic_group.id !== result.group_id) {
                                continue;
                            }
                            if (result.result === "added") {
                                topic_group.topics.push({
                                    "id": null,
                                    "topic_modelling_name": topic_modelling,
                                    "topic_id": result.topic_id,
                                });
                                return;
                            }
                            if (result.result === "removed") {
                                topic_group.topics = topic_group.topics.filter(function (value, index, arr) {
                                    return value.topic_id !== result.topic_id;
                                });
                                return;
                            }
                            alert("Incorrect status code!");
                            return;
                        }
                        alert("Topic group not found!");
                    }
                }
            );
        });

        $('#publicTopicGroupsList').html(generate_topic_group_list(topic_groups_list.public_groups, "public", topic_id));
        $('#topicGroupModal').modal();

        $('.remove-topic').tooltip();
        $('.remove-topic').click(function(e){
            if (confirm("Вы уверены, что хотите удалить группу " + e.target.id)) {
                $.ajax(
                    {
                        url: '/api/topic_group/' + e.target.id.split('removeTopic_')[1],
                        method: 'DELETE',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", csrf_token);
                        },
                        success: function (result) {
                            if (result.status !== 200) {
                                alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                                return;
                            }
                            topic_groups_list.my_groups = topic_groups_list.my_groups.filter(function (value, index, arr) {
                                return value.id !== result.group_id;
                            });
                            topic_groups_list.public_groups = topic_groups_list.public_groups.filter(function (value, index, arr) {
                                return value.id !== result.group_id;
                            });
                            $('#topicGroupModal').modal('hide');
                        }
                    }
                );
            }
        });
    }

    $('.manage-topic-groups').click(function (e) {
        e.preventDefault();
        topic_id = e.target.id.split("manageTopics_")[1];
        manage_topics_onclick(topic_id);
    });

    $('#addGroup').click(function(e) {
        $.ajax(
            {
                url: '/api/topic_group/',
                method: 'POST',
                data: {
                    "name": $('#newGroupName').val(),
                    "topic_modelling": topic_modelling,
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
                    topic_groups_list.my_groups.push({
                        "id": result.id,
                        "name": result.name,
                        "topic_modelling_name": topic_modelling,
                        "is_public": result.is_public,
                        "topics": [],
                    });
                    initialize_groups_select();
                    manage_topics_onclick($('#addGroup').attr('topic_id'));
                }
            }
        );
    });
}
