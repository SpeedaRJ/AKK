function solution(el,solution) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.toLowerCase()+'$')) {
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
    if(counter >= 6)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

function redo() {
    blocks = document.getElementsByClassName("textblock");
    for (var i=0; i < blocks.length; i++)
        blocks[i].style.display="none";
    var b = Math.floor(Math.random()*3)+1;
    document.getElementById("block"+b).style.display="block"
}

$(function(){
    redo();
})