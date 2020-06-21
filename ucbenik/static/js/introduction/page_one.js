function dynamic_name(e) {
    let paras = document.getElementsByClassName("slo_name");
    for(let x in paras) {
        paras[x].innerHTML = e.target.value;
        if(e.target.value === "") {
            paras[x].innerHTML = "____"
            document.getElementById("next").setAttribute("disabled", "disabled");
        }
        else
            document.getElementById("next").removeAttribute("disabled");
    }
}

$(document).ready(function() {
    document.getElementById("name_input").addEventListener("input", function(e) {
        dynamic_name(e);
    });
});