function solution(el,solution) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.toLowerCase()+'\\.*\\!*$')) {
        el.classList.remove("incorrect-text");
        el.classList.add("correct-text");
    } else {
        el.classList.add("incorrect-text");
        el.classList.remove("correct-text");
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct-text") && !paras[x].className.includes("incorrect-text"))
            counter++;
    }
    if(counter === paras.length) {
        document.getElementById("next").removeAttribute("disabled")
        document.getElementById("well_done").hidden = false;
        document.getElementById("inst").hidden = true;
    }
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(function(){
    redo();
})

function redo(e) {
    Array.from(document.getElementsByClassName("textarea")).forEach((element) => {
        if (element.value != "")
            element.classList.remove("correct-text");
        element.value="";
        element.classList.remove("incorrect-text");
    });
}