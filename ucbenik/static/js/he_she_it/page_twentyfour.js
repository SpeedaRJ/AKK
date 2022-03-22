var solutions = {
    "I am not": "I'm not",
    "You are not": "You're not",
    "We are not": "We're not",
    "He is not": "He's not",
    "She is not": "She's not",
    "It is not": "It's not",
    "They are not": "They're not"
}

function redo(e) {
    let table = document.getElementById("help-table");
    table.innerHTML = "";
    var ns = [];
    var adj = [];
    for (var i in solutions)
        adj.push([i]);
    for (i = 0; i < 5; i++) {
        var n = Math.round(Math.random() * (adj.length - 1));
        while (ns.includes(n))
            n = Math.round(Math.random() * (adj.length - 1));
        ns.push(n);
        let word = adj[n];
        let html = '<div class="help row"><button class="col-lg-6 tip" disabled><p>' + word +
            '</p></button><button class="col-lg-6 tip c2">' +
            '<input class="textarea" size="5" onchange="solution(this,' + "'" + word + "'" +
            ')"/></button></div>';

        table.innerHTML += html;
    }
}

function solution(el, s) {
    if (s == "I am not") {
        expression = el.value.trim().replace(/  +/g, ' ').match('^' + solutions[s] + '\.*\!*$');
    }
    else {
        // expression = el.value.toLowerCase().trim().replace(/  +/g, ' ').match(solutions[s].toLowerCase())+'$';
        expression = el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^' + solutions[s].toLowerCase() + '\.*\!*$');
    }

    // if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solutions[s].toLowerCase())+'$') {
    if (expression) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("tip")
    let counter = 0;
    for (let x in paras) {
        if (paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === 5)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}


$(function () {
    redo();
})