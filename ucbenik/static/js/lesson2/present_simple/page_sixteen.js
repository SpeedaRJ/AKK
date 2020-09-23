var questions = [
    "He plays chess.",
    "She knows how to cook.",
    "You have a dog.",
    "He lives alone.",
    "They talk every day.",
    "She often draws.",
    "You are nice.",
    "They live in an apartment.",
    "He hates school.",
    "I am old.",
    "It is 5 o’clock.",
    "You work from home.",
    "You are often late.",
    "It is late.",
    "We are lost."
]

solutions = [
    "Does he play chess",
    "Does she knows how to cook",
    "Do you have a dog",
    "Does he live alone",
    "Do they talk every day",
    "Does she often draw",
    "Are you nice",
    "Do they live in an apartment",
    "Does he hate school",
    "Am I old",
    "What is the time",
    "Do you work from home",
    "Are you often late",
    "Is it late",
    "Are we lost"
]

/*
<div class="row inst space">
                <div class="msg jenny translation" style="width: 100%;">
                    He plays chess. <input class="textarea" onchange="solution(this, 'I doXX love my parents')" type="text" style="width:50%;text-align:center">
                </div>
            </div>
*/
function redo() {
    var div = document.getElementById("questions")
    div.innerHTML="";
    var numbers = [];
    while (numbers.length < 5) {
        var n = Math.floor(Math.random() * questions.length);
        while (numbers.indexOf(n) > -1)
            n = Math.floor(Math.random() * questions.length);
        numbers.push(n);
    }
    for(var i = 0; i < numbers.length; i++) {
        div.innerHTML+='<div class="row"><div class="msg jenny translation full-width">' + questions[numbers[i]]+'</div><div class="msg jenny translation full-width"><input class="textarea" onchange="solution(this, '+"'"+solutions[numbers[i]]+"'"+')" type="text" style="width:90%;"></div></div>'
    }
}

$(function(){
    redo();
})

function solution(el,solution) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.replace("XX","n't").toLowerCase()+'\\?$')) {
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