let solutions = [
    "I'm",
    "We're",
    "They're",
    "She's",
    "He's",
    "You're",
    "It's",
    "You're"
]

function solution(el,n) {
    let parent = el.parentElement;
    if (el.value == solutions[n]) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("slo")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 8)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

function redo() {
    aps = document.getElementById("aps");
    aps.innerHTML='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> I am <input class=textarea onchange="solution(this,0)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> We are <input class=textarea onchange="solution(this,1)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> They are <input class=textarea onchange="solution(this,2)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> She is <input class=textarea onchange="solution(this,3)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> He is <input class=textarea onchange="solution(this,4)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> You (ed.) are  <input class=textarea onchange="solution(this,5)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> It is <input class=textarea onchange="solution(this,6)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 80%; margin-left: 10%;"> You (mn.) are  <input class=textarea onchange="solution(this,7)" style="border-color:#6282B7;background-color: transparent;width: 50%"/></div>'
}

$(function(){
    redo();
})