let selected = false;

function show_country(e) {
    document.getElementById("home_country").style.display = "none";
    if(e.target.innerHTML === "Yes") {
        document.getElementById("home_country").style.display = "block";
        document.getElementById("next").removeAttribute("disabled")
    }
    selected = true;
}

function dynamic_country(e) {
    document.getElementById("slo_county").innerHTML = e.target.value;
    if(e.target.value === "") {
        document.getElementById("slo_county").innerHTML = "_____"
        document.getElementById("next").setAttribute("disabled", "disabled");
        document.getElementById("welcome").style.display = "none";
    }
    if(selected && e.target.value !== "") {
        document.getElementById("next").removeAttribute("disabled");
        document.getElementById("welcome").style.display = "block";

    }
}

$(document).ready(function() {
    document.getElementById("county_input").addEventListener("input", function(e) {
        dynamic_country(e);
    });
});