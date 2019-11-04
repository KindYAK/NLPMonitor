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

// Search by text input
var optionsText = {
    valueNames: ['topic-name', 'topic-words'],
};
var searchEngineText = new List('search-results', optionsText);

typeHandler = function(e){
    table.destroy();
    searchEngineText.search(e.target.value);
    table = init_table();
};
var searchInput = document.querySelector('#topicSearchInput');
searchInput.addEventListener('input', typeHandler);
searchInput.addEventListener('propertychange', typeHandler);

// Search by group select
$('#topicFilterInput').change(function(e){
    table.destroy();
    if(e.target.value === "-1"){
        searchEngineGroup.filter();
    } else {
        topics = null;
        for (topic_group of topic_groups_list.my_groups) {
            if (topic_group.name === e.target.value) {
                topics = topic_group.topics;
                break;
            }
        }
        if(!topics) {
            for (topic_group of topic_groups_list.public_groups) {
                if (topic_group.name === e.target.value) {
                    topics = topic_group.topics;
                    break;
                }
            }
        }
        topic_ids = [];
        for(topic of topics) {
            topic_ids.push(topic.topic_id);
        }
        searchEngineGroup.filter(function(item) {
            return topic_ids.indexOf(item._values['topic-id']) !== -1;
        });
    }
    table = init_table();
});

var optionsGroups = {
    valueNames: ['topic-id',],
};
var searchEngineGroup = new List('search-results', optionsGroups);
