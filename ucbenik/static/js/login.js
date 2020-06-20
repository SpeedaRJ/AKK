let gender = null;

function selectGender(e) {
    if(e.target.id === "mars") {
        gender = "male";
        e.target.style.color = "aqua";
        document.getElementById("venus").style.color = "white";
    } else if(e.target.id === "venus") {
        gender = "female";
        e.target.style.color = "aqua";
        document.getElementById("mars").style.color = "white";
    }
}

$(document).ready(function() {
    document.getElementById("mars").addEventListener("click", function(e) {
        selectGender(e);
    });
    document.getElementById("venus").addEventListener("click", function(e) {
        selectGender(e);
    });
});