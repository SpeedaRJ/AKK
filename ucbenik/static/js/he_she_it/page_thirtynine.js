var eng = [
    "I have",
    "You have",
    "He has",
    "She has",
    "It has",
    "We have",
    "You have",
    "They have"
]
var slo = [
    "Jaz imam",
    "Ti imaš",
    "On ima",
    "Ona ima",
    "Ono ima",
    "Mi imamo",
    "Vi imate",
    "Oni imajo"
]

function redo(e) {
    let table = document.getElementById("help-table");
    let ns = [];
    table.innerHTML="";
    for(i=0; i < 5; i++) {
        var n = Math.round(Math.random() * (eng.length-1));
        while(ns.includes(n)) 
            n = Math.round(Math.random() * (eng.length-1));
        ns.push(n);
        var html =""
        if (Math.random() > 0.5){
            html =  '<div class="help row"><button class="col-lg-6 tip" disabled><p>'+eng[n]+
                    '</p></button><button class="col-lg-6 tip c2">'+
                    '<input class="textarea" size="5" onchange="solution(this,'+"'"+ slo[n] +"'"+
                    ')"/></button></div>';
        } else {
            html =  '<div class="help row"><button class="col-lg-6 tip c2">'+
                    '<input class="textarea" size="5" onchange="solution(this,'+"'"+ eng[n] +"'"+
                    ')"/></button><button class="col-lg-6 tip" disabled><p>'+slo[n]+
                    '</p></button></div>';
        }
        
        table.innerHTML+=html;
    }
}

function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value == solution) {
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


$(function(){
    redo();
})