let next = [false]

function dynamic_age(e) {
    document.getElementById("slo_year").innerHTML = e.target.value;
    if(e.target.value === "") {
        next[0] = false;
        document.getElementById("slo_year").innerHTML = "_____"
    }
    else
        next[0] = true;
    checkNext()
}

function checkNext() {
    if(next[0])
        document.getElementById("next").removeAttribute("disabled");
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(document).ready(function() {
    document.getElementById("year_input").addEventListener("input", function(e) {
        dynamic_age(e);
    });
});