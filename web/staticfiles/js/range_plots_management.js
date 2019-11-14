function run_range_plot_management(topic_modelling, topics, csrf_token) {
    function init_table(){
        return $('#search-results-table').DataTable({
            "paging": true,
            "lengthChange": true,
            "searching": false,
            "ordering": true,
            "order": [],
            "info": true,
            "autoWidth": true,
            "pageLength": 25,
        });
    }

    var table = init_table();

    function request_documents(range_from, range_to) {
        $.ajax(
            {
                url: '/api/range_documents/?topic_modelling=' + topic_modelling +
                    "&date_from=" + range_from + "&date_to=" + range_to +
                    "&topics=" + topics,
                method: 'GET',
                success: function (result) {
                    if (result.status !== 200) {
                        alert("Что-то пошло не так :( Истекла сессия? Попробуйте обновить страницу");
                        return;
                    }
                    // Redraw documents table
                    var table_html = "<div id=\"search-results\">\n" +
                        "                        <table id=\"search-results-table\" class=\"table table-bordered table-hover\">\n" +
                        "                            <thead>\n" +
                        "                            <tr role=\"row\">\n" +
                        "                                <th>Вес в топике</th>\n" +
                        "                                <th>Дата</th>\n" +
                        "                                <th>Заголовок</th>\n" +
                        "                                <th>Источник</th>\n" +
                        "                                <th></th>\n" +
                        "                            </tr>\n" +
                        "                            </thead>\n" +
                        "                            <tbody>";
                    for (doc of result.documents) {
                        table_html += "<tr>";
                        table_html += "<td>" + doc.weight.toString().replace(".", ",") + "</td>";
                        table_html += "<td>" + doc.datetime + "</td>";
                        table_html += "<td>" + doc.title + "</td>";
                        table_html += "<td>" + doc.source + " </td>";
                        table_html += "<td>\n" +
                        "                   <a href=\"/document_view/" + doc.id.toString() + "/\" class=\"nav-link nowrap\">\n" +
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
                    var x = [];
                    var y = [];
                    for (sw of result.source_weights) {
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
                    Plotly.newPlot('source_distribution', data, layout);
                }
            }
        );
        last_req_range_from = range_from;
        last_req_range_to = range_to;
    }

    function rerender_new_range(range_from, range_to, id_to_skip) {
        var plot_ids = ["topic_dynamics", "topic_dynamics_normal", "topic_dynamics_weight"];
        for (var plot_id of plot_ids) {
            if (id_to_skip && plot_id !== id_to_skip) {
                Plotly.relayout(plot_id, 'xaxis.range', [range_from, range_to]);
            }
        }
        last_range_from = range_from;
        last_range_to = range_to;
    }

    var last_range_from = null;
    var last_range_to = null;
    var last_req_range_from = null;
    var last_req_range_to = null;
    setInterval(function () {
        var main_plot = document.getElementById('topic_dynamics');
        var range_from = main_plot.layout.xaxis.range[0];
        var range_to = main_plot.layout.xaxis.range[1];
        if (last_range_to && last_range_from && (last_range_from !== range_from || last_range_to !== range_to)) {
            rerender_new_range(range_from, range_to, "topic_dynamics");
        }
    }, 1000);

    setInterval(function () {
        var main_plot = document.getElementById('topic_dynamics');
        var range_from = main_plot.layout.xaxis.range[0];
        var range_to = main_plot.layout.xaxis.range[1];
        if (last_req_range_from && last_req_range_from && (last_req_range_from !== range_from || last_req_range_from !== range_to)) {
            request_documents(range_from, range_to);
        }
    }, 3333);

    var n_redraw_plot = 0;
    $('.dynamics-plot').on('plotly_relayout',
        function (e) {
            var target = e.target.layout;
            var range_from = target.xaxis.range[0];
            var range_to = target.xaxis.range[1];

            n_redraw_plot += 1;
            if (n_redraw_plot === 0 || n_redraw_plot % 3 !== 0) {
                return;
            }
            rerender_new_range(range_from, range_to, e.target.id);
            if (n_redraw_plot === 0 || n_redraw_plot % 33 !== 0) {
                return;
            }
            request_documents(range_from, range_to);
        }
    );
}
