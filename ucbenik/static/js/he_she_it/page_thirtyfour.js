let solutions = [
    ["Is she happy?"],
    ["He is plump"],
    ["I am not tall", "I'm not tall"],
    ["You are not nice", "You aren't nice"],
    ["Are they our relatives"],
    ["Are we old?"],
    ["She is not happy", "She isn't happy"],
    ["Is he plump"],
    ["Am I tall"],
    ["You are nice", "You're nice"],
    ["They aren't our relatives", "They are not our relatives"],
    ["We are old", "We're old"],
]

function redo() {
    for (let i = 0; i < solutions.length; i++) {
        document.getElementById("a" + i).style.display = "none";
        document.getElementById("ai" + i).value = "";
        document.getElementById("ai" + i).classList.remove("incorrect");
        document.getElementById("ai" + i).classList.remove("correct");
    }
    for (let i = 0; i < 6; i++) {
        if (Math.random() > 0.5) {
            document.getElementById("a" + i).style.display = "inline";
        }
        else {
            document.getElementById("a" + (i + 6)).style.display = "inline";
        }
    }
}

function solution(el, n) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^' + solutions[n].join("|").toLowerCase() + '\\.*\\!*\\?*$')) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for (let x in paras) {
        if (paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === solutions.length / 2)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(function () {
    redo();
})