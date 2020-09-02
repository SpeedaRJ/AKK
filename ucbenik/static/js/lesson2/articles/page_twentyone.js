items = [
    ["an orange", "oranges"],
    ["an avocado", "avocados"],
    ["a city", "cities"],
    ["an enemy", "enemies"],
    ["a fish", "fish"],
    ["a bench", "benches"],
    ["a guy", "guys"],
    ["a toy", "toys"],
    ["a zoo", "zoos"],
    ["a balloon", "balloons"],
    ["a kite", "kites"],
    ["a daisy", "daisies"],
    ["an echo", "echoes"],
    ["an army", "armies"],
    ["a piano", "pianos"],
    ["a person", "people"],
    ["a potato", "potatoes"],
    ["a man", "men"],
    ["a tooth", "teeth"],
    ["a class", "classes"],
    ["a lunch", "lunches"],
    ["a hero", "heroes"],
    ["a radio", "radios"],
    ["a foot", "feet"],
    ["a road", "roads"],
    ["a sheep", "sheep"],
    ["a glass", "glasses"],
    ["a child", "children"],
]

$(function(){
    redo();
})

function redo(e) {
    var convo = document.getElementById('conversation');
    convo.innerHTML="";
    selected = [];
    for (var i = 0; i < 6; i ++) {
        var r = Math.round(Math.random() * items.length);
        while (selected.indexOf(r) > -1 || items[r] == undefined) 
            r = Math.round(Math.random() * items.length);
        selected.push(r)
        convo.innerHTML+='<div class="msg jenny translation" style="text-align: center;"> '+ items[r][0]+' -->  '+'<input class="textarea" size="5" onchange="solution(this,'+"'"+items[r][1]+"'"+')"/>'+' </div>'
    }
    
    
}

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