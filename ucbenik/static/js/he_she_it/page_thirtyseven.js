$(document).ready(function () {
    document.getElementById("next").setAttribute("disabled", "disabled");
});

function check() {

    let result1 = $("#textarea1").val();
    let result2 = $("#textarea2").val();

    if (result1 == "has") {
        document.getElementById("textarea1").style.color = "greenyellow";
    }

    if (result2 == "has") {
        document.getElementById("textarea2").style.color = "greenyellow";
    }

    if (result1 == "has" && result2 == "has") {
        document.getElementById("next").removeAttribute("disabled");
    }
    else {
        if (result1 != "has") {
            document.getElementById("textarea1").style.color = "red";
        }

        if (result2 != "has") {
            document.getElementById("textarea2").style.color = "red";
        }
    }
}