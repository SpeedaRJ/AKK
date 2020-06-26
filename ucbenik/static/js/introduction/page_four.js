function show_country(e) {
    document.getElementById("home_country").style.display = "none";
    if(e.target.innerHTML === "No") {
        document.getElementById("home_country").style.display = "block";
        if(document.getElementById("county_input").innerHTML === "")
            document.getElementById("next").setAttribute("disabled", "disabled");
            document.getElementById("welcome").style.display = "none";
    }
    if(e.target.innerHTML === "Yes") {
        document.getElementById("welcome").style.display = "block";
        document.getElementById("next").removeAttribute("disabled");
    }
}

function dynamic_country(e) {
    document.getElementById("slo_county").innerHTML = e.target.value;
    if(e.target.value === "") {
        document.getElementById("slo_county").innerHTML = "_____"
        document.getElementById("next").setAttribute("disabled", "disabled");
        document.getElementById("welcome").style.display = "none";
    }
    else
        document.getElementById("next").removeAttribute("disabled");
}

$(document).ready(function() {
    document.getElementById("county_input").addEventListener("input", function(e) {
        dynamic_country(e);
    });
});