function solution(el,solution) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.replace("XX","n't").toLowerCase()+'\\.*\\!*$')) {
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
    if(counter === 5)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}