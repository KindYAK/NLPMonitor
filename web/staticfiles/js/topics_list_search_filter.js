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
$('#topicSearchInput').val("");
var table = init_table();

// Search+Filter function
function search_filter(){
    table.destroy();

    searchEngine.search($('#topicSearchInput').val());
    if($('#topicFilterInput').val() === "-1"){
        searchEngine.filter();
    } else {
        topics = null;
        for (topic_group of topic_groups_list.my_groups) {
            if (topic_group.name === $('#topicFilterInput').val()) {
                topics = topic_group.topics;
                break;
            }
        }
        if(!topics) {
            for (topic_group of topic_groups_list.public_groups) {
                if (topic_group.name === $('#topicFilterInput').val()) {
                    topics = topic_group.topics;
                    break;
                }
            }
        }
        topic_ids = [];
        for(topic of topics) {
            topic_ids.push(topic.topic_id);
        }
        searchEngine.filter(function(item) {
            return topic_ids.indexOf(item._values['topic-id']) !== -1;
        });
    }

    table = init_table();
}

// Search by text input
var optionsText = {
    valueNames: ['topic-name', 'topic-words', 'topic-id', ],
};
var searchEngine = new List('search-results', optionsText);

var searchInput = document.querySelector('#topicSearchInput');
searchInput.addEventListener('input', search_filter);
searchInput.addEventListener('propertychange', search_filter);

// Search by group select
$('#topicFilterInput').change(search_filter);
