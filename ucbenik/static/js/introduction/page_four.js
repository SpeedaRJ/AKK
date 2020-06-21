function show_country(e) {
    document.getElementById("home_country").style.display = "block";
    if(e.target.innerHTML === "No") {
        document.getElementById("home_country").style.display = "none";
        document.getElementById("next").removeAttribute("disabled")
    }
    document.getElementById("response").style.display = "block";
}

function dynamic_country(e) {
    document.getElementById("slo_county").innerHTML = e.target.value;
    if(e.target.value === "") {
        document.getElementById("slo_county").innerHTML = "_____"
        document.getElementById("next").setAttribute("disabled", "disabled");
    }
    document.getElementById("next").removeAttribute("disabled");
}

$(document).ready(function() {
    document.getElementById("county_input").addEventListener("input", function(e) {
        dynamic_country(e);
    });
});