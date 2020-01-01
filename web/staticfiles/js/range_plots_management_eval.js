function generate_plot_data_for_posneg_sources(sources){
    for (source of sources) {
        var total_source = source.negative + source.neutral + source.positive;
        source.negative_percent = (source.negative / total_source * 100).toFixed(2);
        source.neutral_percent = (source.neutral / total_source * 100).toFixed(2);
        source.positive_percent = (source.positive / total_source * 100).toFixed(2);
    }

    sources.sort(function (a, b) {
        return b.negative_percent - a.negative_percent;
    });

    var keys = [];

    var negatives_by_source = [];
    var neutrals_by_source = [];
    var positives_by_source = [];

    var negatives_by_source_percents = [];
    var neutrals_by_source_percents = [];
    var positives_by_source_percents = [];

    for (source of sources) {
        keys.push(source.key);
        negatives_by_source.push(source.negative);
        neutrals_by_source.push(source.neutral);
        positives_by_source.push(source.positive);
        negatives_by_source_percents.push(source.negative_percent);
        neutrals_by_source_percents.push(source.neutral_percent);
        positives_by_source_percents.push(source.positive_percent);
    }

    var data = [
        {
            x: keys,
            y: negatives_by_source_percents,
            type: 'bar',
            'name': 'Негативные',
            marker: {
                color: '#d3322b',
            },
        },
        {
            x: keys,
            y: neutrals_by_source_percents,
            type: 'bar',
            'name': 'Нейтральные',
            marker: {
                color: '#fee42c',
            },
        },
        {
            x: keys,
            y: positives_by_source_percents,
            type: 'bar',
            'name': 'Позитивные',
            marker: {
                color: '#23964f',
            }
        }
    ];
    return data;
}


function run_range_plot_management(criterions, topic_modelling, topic_weight_threshold, keyword,
                                    group_id, criterion_q, action_q, value_q, plot_ids) {
    var main_plot_id = "value_dynamics";

    function rerender_new_range(range_from, range_to, id_to_skip) {
        for (var plot_id of plot_ids) {
            if (id_to_skip && plot_id !== id_to_skip) {
                Plotly.relayout(plot_id, 'xaxis.range', [range_from, range_to]);
            }
        }
        last_range_from = range_from;
        last_range_to = range_to;
    }

    function init_table() {
        return $('#search-results-table').DataTable({
            "paging": true,
            "lengthChange": true,
            "searching": false,
            "ordering": true,
            "order": [
                [0, 'desc'],
                [1, 'desc'],
                [2, 'desc'],
            ],
            "info": true,
            "autoWidth": true,
            "pageLength": 25,
        });
    }

    function rerender_table_plot(result) {
        // Redraw documents table
        var table_html = "<div id=\"search-results\">\n" +
            "                        <table id=\"search-results-table\" class=\"table table-bordered table-hover\">\n" +
            "                            <thead>\n" +
            "                            <tr role=\"row\">\n";
        for(criterion of criterions){
            table_html += "                 <th>" + criterion.fields.name + "</th>\n";
        }
        table_html += "                      <th>Дата</th>\n" +
            "                                <th>Заголовок</th>\n" +
            "                                <th>Источник</th>\n" +
            "                                <th></th>\n" +
            "                            </tr>\n" +
            "                            </thead>\n" +
            "                            <tbody>";
        for (doc of result.documents) {
            table_html += "<tr>";
            for (k in doc) {
                if(k === "document"){
                    continue;
                }
                table_html += "<td>" + doc[k].toFixed(3).toString().replace(".", ",") + "</td>";
            }
            table_html += "<td>" + doc.document.datetime + "</td>";
            table_html += "<td>" + doc.document.title + "</td>";
            table_html += "<td>" + doc.document.source + " </td>";
            table_html += "<td>\n" +
                "                   <a href=\"/document_view/" + doc.document.id.toString() + "/\" class=\"nav-link nowrap\">\n" +
                "                       <i class=\"nav-icon fas fa-eye\" style=\"font-size: 36px;\"\n" +
                "                          data-toggle=\"tooltip\" data-placement=\"top\" title=\"Просмотреть новость\"></i>\n" +
                "                   </a>\n" +
                "               </td>";
            table_html += "</tr>";
        }
        table_html += "</tbody>\n" +
            "     </table>";
        table.destroy();
        $('#search-results').html(table_html);
        table = init_table();

        // Redraw source distribution plot
        for (criterion_id in result.source_weights) {
            var value_range_from = null;
            for(criterion of criterions){
                if(criterion.pk == criterion_id){
                    value_range_from = criterion.fields.value_range_from;
                    break;
                }
            }
            if(value_range_from >= 0){
                var x = [];
                var y = [];
                for (sw of result.source_weights[criterion_id]) {
                    x.push(sw.source);
                    y.push(sw.weight);
                }
                var data = [
                    {
                        x: x,
                        y: y,
                        type: 'bar'
                    }
                ];
                var layout = {
                    showlegend: false,
                    bargap: 0.025
                };
            } else {
                var layout = {
                    showlegend: false,
                    bargap: 0.025,
                    barmode: 'stack',
                };
                var data = generate_plot_data_for_posneg_sources(result.source_weights[criterion_id]);
            }
            Plotly.newPlot('source_distribution_' + criterion_id.toString(), data, layout, {responsive: true});
        }

        // Redraw posneg plot
        for (criterion_id in result.source_weights) {
            var value_range_from = null;
            for (criterion of criterions) {
                if (criterion.pk == criterion_id) {
                    value_range_from = criterion.fields.value_range_from;
                    criterion_name = criterion.fields.name;
                    break;
                }
            }
            if(value_range_from >= 0){
                continue;
            }
            var data = [
                {
                    x: ["Негатив", "Нейтральные", "Позитив"],
                    y: result.posneg_distribution[criterion_id],
                    marker: {
                        color: ['#d3322b', '#fee42c', '#23964f']
                    },
                    type: 'bar'
                }
            ];
            var layout = {
                title: criterion_name,
                showlegend: false,
                bargap: 0.025,
            };
            Plotly.newPlot('posneg_distribution_' + criterion_id, data, layout, {responsive: true});
        }

        // Redraw main topics
        var table_html = "<div id=\"main-topics\">\n";
        for (criterion of criterions) {
            table_html += "<h4>" + criterion.fields.name + " - главные топики по положительному влиянию</h4>" +
                "           <table id=\"main-topics-table\" class=\"table table-bordered table-hover\">\n" +
                "                   <thead>\n" +
                "                      <tr role='row'>" +
                "                          <th>Топик</th>\n" +
                "                          <th>Прогнозируемая резонансность</th>\n" +
                "                          <th>Прогнозируемая продолжительность</th>\n" +
                "                          <th>Тренд</th>\n" +
                "                          <th>Вес</th>\n" +
                "                          <th></th>" +
                "                      </tr>\n" +
                "                    </thead>\n" +
                "                <tbody>";
            for (topic of result.posneg_top_topics[criterion.pk]) {
                table_html += "<tr>";
                table_html += "<td id='name_" + criterion.id + "_" + topic.info.id + "'>" + topic.info.name + "</td>";

                table_html += "<td id='resonance_" + criterion.id + "_" + topic.info.id + "'>";
                if('resonance_score' in topic){
                    table_html += topic.resonance_score.toFixed(3).toString().replace(".", ",");
                } else {
                    table_html += "Фоновый топик";
                }
                table_html += "</td>";

                table_html += "<td id='period_" + criterion.id + "_" + topic.info.id + "'>";
                if('period_days' in topic){
                    table_html += topic.period_days.toFixed(1).toString().replace(".", ",");
                    table_html += " дней (Score: " + topic.period_score.toFixed(3).toString().replace(".", ",") + ")"
                } else {
                    table_html += "Фоновый топик";
                }
                table_html += "</td>";

                table_html += "<td id='trend_" + criterion.id + "_" + topic.info.id + "'>";
                if('trend_score' in topic && topic.trend_score !== 0){
                    table_html += topic.trend_score.toFixed(3).toString().replace(".", ",");
                    if(topic.trend_score > 0){
                        table_html += '<div style="text-align: center;">' +
                            '               <i class="fas fa-arrow-up"></i>' +
                            '          </div>';
                    } else {
                        table_html += '<div style="text-align: center;">' +
                            '               <i class="fas fa-arrow-down"></i>' +
                            '          </div>';
                    }
                }
                table_html += "</td>";

                table_html += "<td id='weight_" + criterion.id + "_" + topic.info.id + "'>" + topic.weight.toFixed(3).toString().replace(".", ",") + "</td>";

                table_html += "<td>\n" +
                    "              <a href='/topicmodelling/topic_documents_list/" + topic_modelling + "/" + topic.info.id +"?topic_name=" + topic.info.name + "&topic_weight_threshold=" + topic_weight_threshold.toString() + "' class=\"nav-link nowrap\">\n" +
                    "                  <i class=\"nav-icon fas fa-eye\" style=\"font-size: 24px;\"" +
                    "                     data-toggle=\"tooltip\" data-placement=\"top\" title=\"Анализ по тематике\"></i>\n" +
                    "               </a>\n" +
                    "          </td>";

                table_html += "</tr>";
            }
            table_html += "</tbody>\n" +
                "     </table>";

            table_html += "<h4>" + criterion.fields.name + " - главные топики по отрицательному влиянию</h4>" +
                "           <table id=\"main-topics-table\" class=\"table table-bordered table-hover\">\n" +
                "                   <thead>\n" +
                "                      <tr role=\"row\">\n" +
                "                          <th>Топик</th>\n" +
                "                          <th>Прогнозируемая резонансность</th>\n" +
                "                          <th>Прогнозируемая продолжительность</th>\n" +
                "                          <th>Тренд</th>\n" +
                "                          <th>Вес</th>\n" +
                "                          <th></th>" +
                "                      </tr>\n" +
                "                    </thead>\n" +
                "                <tbody>";
            for (topic of result.posneg_bottom_topics[criterion.pk]) {
                table_html += "<tr>";
                table_html += "<td id='name_" + criterion.id + "_" + topic.info.id + "'>" + topic.info.name + "</td>";

                table_html += "<td id='resonance_" + criterion.id + "_" + topic.info.id + "'>";
                if('resonance_score' in topic){
                    table_html += topic.resonance_score.toFixed(3).toString().replace(".", ",");
                } else {
                    table_html += "Фоновый топик";
                }
                table_html += "</td>";

                table_html += "<td id='period_" + criterion.id + "_" + topic.info.id + "'>";
                if('period_days' in topic){
                    table_html += topic.period_days.toFixed(1).toString().replace(".", ",");
                    table_html += " дней (Score: " + topic.period_score.toFixed(3).toString().replace(".", ",") + ")"
                } else {
                    table_html += "Фоновый топик";
                }
                table_html += "</td>";

                table_html += "<td id='trend_" + criterion.id + "_" + topic.info.id + "'>";
                if('trend_score' in topic && topic.trend_score !== 0){
                    table_html += topic.trend_score.toFixed(3).toString().replace(".", ",");
                    if(topic.trend_score > 0){
                        table_html += '<div style="text-align: center;">' +
                            '               <i class="fas fa-arrow-up"></i>' +
                            '          </div>';
                    } else {
                        table_html += '<div style="text-align: center;">' +
                            '               <i class="fas fa-arrow-down"></i>' +
                            '          </div>';
                    }
                }
                table_html += "</td>";

                table_html += "<td id='weight_" + criterion.id + "_" + topic.info.id + "'>" + topic.weight.toFixed(3).toString().replace(".", ",") + "</td>";

                table_html += "<td>\n" +
                    "              <a href='/topicmodelling/topic_documents_list/" + topic_modelling + "/" + topic.info.id +"?topic_name=" + topic.info.name + "&topic_weight_threshold=" + topic_weight_threshold.toString() + "' class=\"nav-link nowrap\">\n" +
                    "                  <i class=\"nav-icon fas fa-eye\" style=\"font-size: 24px;\"" +
                    "                     data-toggle=\"tooltip\" data-placement=\"top\" title=\"Анализ по тематике\"></i>\n" +
                    "               </a>\n" +
                    "          </td>";

                table_html += "</tr>";
            }
            table_html += "</tbody>\n" +
                "     </table>";
        }
        $('#main-topics').html(table_html);
        for (criterion of criterions) {
            for (topic of result.posneg_top_topics[criterion.pk]) {
                if(!('resonance_score' in topic)){
                    continue;
                }
                $('#resonance_' + criterion.id + '_' + topic.info.id).css('background-color', colorScale(topic.resonance_score));
                $('#period_' + criterion.id + '_' + topic.info.id).css('background-color', colorScale(topic.period_score));
                if(topic.trend_score && topic.trend_score !== 0) {
                    $('#trend_' + criterion.id + '_' + topic.info.id).css('background-color', colorScale(topic.trend_score));
                }
            }
        }
        for (criterion of criterions) {
            for (topic of result.posneg_bottom_topics[criterion.pk]) {
                if(!('resonance_score' in topic)){
                    continue;
                }
                $('#resonance_' + criterion.id + '_' + topic.info.id).css('background-color', colorScaleNeg(topic.resonance_score));
                $('#period_' + criterion.id + '_' + topic.info.id).css('background-color', colorScaleNeg(topic.period_score));
                if(topic.trend_score && topic.trend_score !== 0) {
                    $('#trend_' + criterion.id + '_' + topic.info.id).css('background-color', colorScaleNeg(topic.trend_score));
                }
            }
        }
    }

    function request_documents(range_from, range_to) {
        var url = '/api/range_documents/?topic_modelling=' + topic_modelling +
                    "&date_from=" + range_from +
                    "&date_to=" + range_to +
                    "&topic_modelling=" + topic_modelling +
                    "&topic_weight_threshold=" + topic_weight_threshold.toString();
        for (criterion of criterions){
            url += "&criterions=" + criterion.pk.toString()
        }
        url += "&keyword=" + keyword +
                    "&group=" + group_id +
                    "&criterion_q=" + criterion_q +
                    "&action_q=" + action_q +
                    "&value_q=" + value_q +
                    "&type=criterions";
        $.ajax(
            {
                url: url,
                method: 'GET',
                success: function (result) {
                    if (result.status !== 200) {
                        alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                        return;
                    }
                    rerender_table_plot(result);
                },
                error: function (result) {
                    alert("Возможно отсутствует соединение с интернетом. Если проблема повторяется, обратитесь к администратору системы");
                }
            }
        );
        last_req_range_from = range_from;
        last_req_range_to = range_to;
    }

    var table = init_table();
    var last_range_from = null;
    var last_range_to = null;
    var last_req_range_from = null;
    var last_req_range_to = null;
    var n_redraw_plot = 0;

    setInterval(function () {
        var main_plot = document.getElementById(main_plot_id);
        var range_from = main_plot.layout.xaxis.range[0];
        var range_to = main_plot.layout.xaxis.range[1];
        if (last_range_to && last_range_from && (last_range_from !== range_from || last_range_to !== range_to)) {
            rerender_new_range(range_from, range_to, main_plot_id);
        }
    }, 3333);

    setInterval(function () {
        var main_plot = document.getElementById(main_plot_id);
        var range_from = main_plot.layout.xaxis.range[0];
        var range_to = main_plot.layout.xaxis.range[1];
        if (last_req_range_from && last_req_range_to && (last_req_range_from !== range_from || last_req_range_to !== range_to)) {
            request_documents(range_from, range_to);
        }
    }, 3333);

    $('.dynamics-plot').on('plotly_relayout',
        function (e) {
            var target = e.target.layout;
            var range_from = target.xaxis.range[0];
            var range_to = target.xaxis.range[1];

            n_redraw_plot += 1;
            if (n_redraw_plot !== 0 && n_redraw_plot % 3 === 0) {
                rerender_new_range(range_from, range_to, e.target.id);
            }
            if (n_redraw_plot === 1 || n_redraw_plot % 33 === 0) {
                request_documents(range_from, range_to);
            }
        }
    );
}
