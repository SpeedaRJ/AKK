items = [
    ["A nose is pink", "Noses are pink"],
    ["A fly is annoying", "Flies are annoying"],
    ["A donkey is loud", "Donkeys are loud"],
    ["An address is long", "Addresses are long"],
    ["A potato is sweet", "Potatoes are sweet"],
    ["A woman is tall", "Women are tall"],
    ["An orange is orange", "Oranges are orange"],
    ["A spy is smart", "Spies are smart"],
    ["A man is fat", "Men are fat"],
    ["A princess is pretty", "Princesses are pretty"],
    ["A watch is wrong", "Watches are wrong"],
    ["A mouse is quiet", "Mice are quiet"],
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