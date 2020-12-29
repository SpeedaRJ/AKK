let solutions = [
    "this",
    "those",
    "these",
    "that",
]

function solution(el,n) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().replace(/  +/g, ' ').match('^'+solutions[n].toLowerCase()+'$')) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("slo")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === solutions.length)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(document).ready(function() {
    $("#S1").val("hers");
    $("#S1").attr("readonly", true);
})