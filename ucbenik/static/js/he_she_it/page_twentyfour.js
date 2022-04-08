var solutions = {
    "I am not": "I'm not",
    "You are not": "You aren't",
    "We are not": "We aren't",
    "He is not": "He isn't",
    "She is not": "She isn't",
    "It is not": "It isn't",
    "They are not": "They aren't"
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
        el.parentElement.classList.remove("incorrect");
        el.parentElement.classList.add("correct");
    } else {
        el.parentElement.classList.add("incorrect");
        el.parentElement.classList.remove("correct");
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