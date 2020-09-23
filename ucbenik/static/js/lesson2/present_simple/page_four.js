function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.toLowerCase()+'\\.*\\!*$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("tip")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 5)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}