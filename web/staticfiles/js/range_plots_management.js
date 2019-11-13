function run_range_plot_management(topic_modelling, topics, csrf_token) {
    function rerender_new_range(range_from, range_to, id_to_skip) {
        var plot_ids = ["topic_dynamics", "topic_dynamics_normal", "topic_dynamics_weight"];
        for (var plot_id of plot_ids) {
            if (id_to_skip && plot_id !== id_to_skip) {
                Plotly.relayout(plot_id, 'xaxis.range', [range_from, range_to]);
            }
        }
        last_range_from = range_from;
        last_range_to = range_to;

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
                    console.log(result);
                }
            }
        );
    }

    var last_range_from = null;
    var last_range_to = null;
    setInterval(function () {
        var main_plot = document.getElementById('topic_dynamics');
        var range_from = main_plot.layout.xaxis.range[0];
        var range_to = main_plot.layout.xaxis.range[1];
        if (last_range_to && last_range_from && (last_range_from !== range_from || last_range_to !== range_to)) {
            rerender_new_range(0, 1, null);
        }
    }, 1111);

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
        }
    );
}
