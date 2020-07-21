let gender = null;
let firsttime = true;

function selectGender(e) {
    if(firsttime){
        document.getElementById("RegisterButton").disabled = false;
        firsttime=false;
    }
    if(e.target.id === "mars") {
        gender = "male";
        document.getElementById(e.target.id).style.color = "aqua";
        document.getElementById("venus").style.color = "white";
        document.getElementById("Sex").value="M";
    } else if(e.target.id === "venus") {
        gender = "female";
        document.getElementById(e.target.id).style.color = "aqua";
        document.getElementById("mars").style.color = "white";
        document.getElementById("Sex").value="F";
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

