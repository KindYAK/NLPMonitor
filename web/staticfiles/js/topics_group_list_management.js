var topic_groups_list = null;

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
            list_html += "</li>";
        }
        list_html += "</ul>";
        return list_html;
    }

    $('.manage-topic-groups').click(function (e) {
        e.preventDefault();
        topic_id = e.target.id.split("manageTopics_")[1];

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
    });

    $('#addGroup').click(function() {
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
                    $('#topicGroupModal').modal('hide');
                }
            }
        );
    });
}
