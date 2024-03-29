function solution(el,solution) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.replace('XX',"don't").toLowerCase()+'\\.*\\!*$')) {
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
    if(counter === paras.length) {
        document.getElementById("next").removeAttribute("disabled")
        document.getElementById("well_done").hidden = false;
        document.getElementById("inst").hidden = true;
    }
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}