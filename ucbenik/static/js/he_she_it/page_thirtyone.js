let solutions = [
    ["I am"],
    ["she is"],
    ["you are"],
    ["they are"],
    ["we are"],
    ["he is"],
    ["it is"],
    ["they are"],
    ["I am not", "I'm not"],
    ["she isn't", "she is not"],
    ["you aren't", "you are not"],
    ["they aren't", "they are not"],
    ["we aren't", "we are not"],
    ["he isn't", "he is not"],
    ["it isn't", "it is not"],
    ["they aren't", "they are not"],
]

function redo() {
    for (i = 0; i < solutions.length; i++)
        document.getElementById("a"+i).style.display="none";
    for (i = 0; i < 8; i++) {
        if(Math.random() > 0.5)
            document.getElementById("a"+i).style.display="inline";
        else
        document.getElementById("a"+(i+8)).style.display="inline";
    }
}

function solution(el,n) {
    if (el.value.match(solutions[n].join("|")) ) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === solutions.length/2)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(function(){
    redo();
})