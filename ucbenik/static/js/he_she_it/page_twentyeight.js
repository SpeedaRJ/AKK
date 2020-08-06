let solutions = [
    "Is she slender",
    "Is he fat",
    "Are you happy",
    "Are they sad",
    "Am I short",
    "Are we tall"
]

function solution(el,n) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').replace(/  +/g, ' ').match('^'+solutions[n].toLowerCase()+'\\?*$')) {
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
    if(counter === solutions.length)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

function redo() {
    aps = document.getElementById("aps");
    aps.innerHTML='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh"> She is slender. </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,0)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh""> He isn'+"'"+'t fat </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,1)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh""> You are happy. </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,2)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh""> They aren'+"'"+'t sad. </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,3)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh""> I am short. </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,4)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
    aps.innerHTML+='<div class="msg jenny slo in" style="width: 40%;float:left;margin-left:0;height:6vh""> We are tall. </div><div class="msg jenny slo in" style="width: 40%;float:right;height:6vh""><input class=textarea onchange="solution(this,5)" style="border-color:#6282B7;background-color: transparent;width: 100%"/></div>'
}

$(function(){
    redo();
})