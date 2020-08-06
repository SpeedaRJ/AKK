let solutions = [
    ["I am happy"],
    ["she is talented"],
    ["you are my teacher",""],
    ["they are from Canada",""],
    ["we are at home",""],
    ["he is my boyfriend",""],
    ["it is dangerous",""],
    ["they are right",""],
    ["I'm not happy","I am not happy"],
    ["she isn't talented","she is not talented"],
    ["you aren't my teacher","you are not my teacher"],
    ["they aren't from Canada","they are not from Canada"],
    ["we aren't at home","we are not home"],
    ["he isn't my boyfriend","he is not my boyfriend"],
    ["it isn't dangerous","it is not dangerous"],
    ["they aren't right","they are not right"]
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
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solutions[n].join("|").toLowerCase()+'\\.*\\!*$') ) {
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