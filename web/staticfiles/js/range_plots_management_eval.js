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
        // TODO Separate function
        for (criterion_id in result.source_weights) {
            var value_range_from = null;
            for(criterion of criterions){
                if(criterion.pk == criterion_id){
                    value_range_from = criterion.value_range_from;
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
                for (source of result.source_weights[criterion_id]){
                    var total_source = source.negative + source.neutral + source.positive;
                    source.negative_percent = (source.negative/total_source * 100).toFixed(2);
                    source.neutral_percent = (source.neutral/total_source * 100).toFixed(2);
                    source.positive_percent = (source.positive/total_source * 100).toFixed(2);
                }

                sources.sort(function(a, b){
                    return b.negative_percent - a.negative_percent;
                });

                var keys = [];

                var negatives_by_source = [];
                var neutrals_by_source = [];
                var positives_by_source = [];

                var negatives_by_source_percents = [];
                var neutrals_by_source_percents = [];
                var positives_by_source_percents = [];

                for (source of sources){
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
                var layout = {
                    showlegend: false,
                    bargap: 0.025,
                    barmode: 'stack',
                };
            }
            Plotly.newPlot('source_distribution_' + criterion_id.toString(), data, layout, {responsive: true});
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
