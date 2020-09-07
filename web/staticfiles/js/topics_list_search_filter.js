// Initital stuff
function init_table(){
    return $('#search-results-table').DataTable({
        "paging": false,
        "lengthChange": true,
        "searching": false,
        "ordering": true,
        "order": [],
        "info": true,
        "autoWidth": true,
    });
}
$('#topicSearchInput').val("");
var table = init_table();

// Search+Filter function
var typed = 0;
var last_search = "";
function search_filter(){
    table.destroy();
    let search_query = $('#topicSearchInput').val();
    searchEngine.search(search_query);
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
    last_search = search_query;
}
function search_filter_type_wrapper(){
    typed += 1;
    if(typed % 5 == 0 && last_search != $('#topicSearchInput').val()){
        search_filter();
    }
}

setInterval(function () {
    if(last_search != $('#topicSearchInput').val()){
        search_filter();
    }
}, 1111);

// Search by text input
var optionsText = {
    valueNames: ['topic-name', 'topic-words', 'topic-id', ],
};
var searchEngine = new List('search-results', optionsText);

var searchInput = document.querySelector('#topicSearchInput');
searchInput.addEventListener('input', search_filter_type_wrapper);
$('#topicSearchInput').change(search_filter);

// Search by group select
$('#topicFilterInput').change(search_filter);

// Getting topics group detail - form management
$('#topicGroupDetailSubmit').click(function(e){
    e.preventDefault();

    var topic_ids = [];
    for (topic of searchEngine.matchingItems){
        topic_ids.push(topic._values['topic-id']);
    }
    $('#topicGroupFiltered').val(JSON.stringify(topic_ids));

    $('#topicGroupDetailForm').submit();
});
