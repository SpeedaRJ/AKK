let next = false

function dynamic_age(e) {
    document.getElementById("slo_age").innerHTML = e.target.value;
    if(e.target.value === "") {
        next = false;
        document.getElementById("slo_age").innerHTML = "_____"
    }
    else
        next = true;
    checkNext()
}

function dynamic_county(e) {
    document.getElementById("slo_birth_place").innerHTML = e.target.value;
    if(e.target.value === "") {
        next = false;
        document.getElementById("slo_birth_place").innerHTML = "_____"
    }
    else
        next = true;
    checkNext()
}

function checkNext() {
    if(next)
        document.getElementById("next").removeAttribute("disabled");
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(document).ready(function() {
    try {
        document.getElementById("age_input").addEventListener("input", function(e) {
            dynamic_age(e);
        });
    } catch(e){}
    try {
    document.getElementById("birth_place_input").addEventListener("input", function(e) {
        dynamic_county(e);
    });
    } catch(e){}
});