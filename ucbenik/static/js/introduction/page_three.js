let next = [false, false]

function dynamic_age(e) {
    document.getElementById("slo_age").innerHTML = e.target.value;
    if(e.target.value === "") {
        next[0] = false;
        document.getElementById("slo_age").innerHTML = "_____"
    }
    else
        next[0] = true;
    checkNext()
}

function dynamic_county(e) {
    document.getElementById("slo_birth_place").innerHTML = e.target.value;
    if(e.target.value === "") {
        next[1] = false;
        document.getElementById("slo_birth_place").innerHTML = "_____"
    }
    else
        next[1] = true;
    checkNext()
}

function checkNext() {
    if(next[0] && next[1])
        document.getElementById("next").removeAttribute("disabled");
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(document).ready(function() {
    document.getElementById("age_input").addEventListener("input", function(e) {
        dynamic_age(e);
    });
    document.getElementById("birth_place_input").addEventListener("input", function(e) {
        dynamic_county(e);
    });
});