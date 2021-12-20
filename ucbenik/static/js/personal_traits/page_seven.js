function solution(final) {
    var inputs = document.getElementsByClassName("textarea");
    if (inputs[0].value != "", inputs[1].value != "")
        document.getElementById("div_two").removeAttribute("hidden");
    if (final && final.value.toLowerCase().includes("what are you like")) {
        document.getElementById("div_three").removeAttribute("hidden");
        document.getElementById("next").removeAttribute("disabled");
    }
}