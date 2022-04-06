var pro = [
    "I",
    "You (ed.) ",
    "We",
    "He",
    "She",
    "It",
    "You (mn.)",
    "They"
];
var verb = [
    "am",
    "are",
    "are",
    "is",
    "is",
    "is",
    "are",
    "are"
];

function redo() {
    let ns = [];
    let fillin = document.getElementById('fillin');
    fillin.innerHTML = "";
    for (let i = 0; i < pro.length; i++) {
        var html = '<div class="msg user fill">' + pro[i] +
            '<input class=textarea onchange="solution(this,' + "'" + verb[i] + "'" + ')"/>.</div>';
        fillin.innerHTML += html;
    }
}

function solution(el, solution) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').replace('velikodušen', 'radodaren').replace('nesramen', 'neprijazen').match('^' + solution.toLowerCase() + '\.*\!*$$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("fill")
    let counter = 0;
    for (let x in paras) {
        if (paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === 8)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}


$(function () {
    redo();
})