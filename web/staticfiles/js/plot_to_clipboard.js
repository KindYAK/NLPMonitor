function get_time_series(plot_id){
    let plot = document.getElementById(plot_id).data["0"];
    output = "";
    for(i = 0; i < plot.x.length; i++){
        let d = new Date(plot.x[i]);
        output += d.getDate().toString() + "." + d.getMonth() + "." + d.getFullYear() + "\t"
                    + plot.y[i].toString().replace(".", ",") + "\n";
    }
    return output;
}

function get_time_series_posneg(plot_id){
    let plot_pos = document.getElementById(plot_id).data["0"];
    let plot_neg = document.getElementById(plot_id).data["1"];
    output = "";
    for(i = 0; i < plot_pos.x.length; i++){
        let d = new Date(plot_pos.x[i]);
        output += d.getDate().toString() + "." + d.getMonth() + "." + d.getFullYear() + "\t"
                    + plot_pos.y[i].toString().replace(".", ",") + "\t" + plot_neg.y[i].toString().replace(".", ",") + "\n";
    }
    return output;
}

function get_bar(plot_id){
    let plot = document.getElementById(plot_id).data["0"];
    output = "";
    for(i = 0; i < plot.x.length; i++){
        output += plot.x[i].toString() + "\t" + plot.y[i].toString().replace(".", ",") + "\n";
    }
    return output;
}

function get_bar_posneg(plot_id){
    let plot_pos = document.getElementById(plot_id).data["2"];
    let plot_neut = document.getElementById(plot_id).data["1"];
    let plot_neg = document.getElementById(plot_id).data["0"];
    output = "";
    for(i = 0; i < plot_pos.x.length; i++){
        output += plot_pos.x[i].toString() + "\t"
            + plot_pos.y[i].toString().replace(".", ",") + "\t" + plot_neut.y[i].toString().replace(".", ",") + "\t" + plot_neg.y[i].toString().replace(".", ",") + "\n";
    }
    return output;
}
