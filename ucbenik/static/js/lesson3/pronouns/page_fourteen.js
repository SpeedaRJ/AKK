let solutions = [
    "this",
    "those",
    "these",
    "that",
]

var index = 0;
var lists = ["first","second","third", "fourth", "fifth", "sixth", "seventh", "eight", "ninth", "tenth"];

pass = [false, false]

function solution(el,n) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().replace(/  +/g, ' ').match('^'+solutions[n].toLowerCase()+'$')) {
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
            console.log(counter)
    if(counter === solutions.length){
        pass[0] = true;
        checkCorrectness();
    }
    else {
        pass[0] = false;
        checkCorrectness();
    }
}

function changelist() {
     index++;
     if(index == 9){
        pass[1] = true;
        document.getElementById("next-list").setAttribute("disabled", "disabled");
        ocument.getElementById("next-list").setAttribute("hidden", "hidden");
        checkCorrectness();
     }
     document.getElementById(lists[index - 1]).setAttribute("hidden", "hidden");
     document.getElementById(lists[index]).removeAttribute("hidden");
     checkCorrectness();
}

function checkCorrectness() {
    if(pass[1]) {
        document.getElementById("next").removeAttribute("disabled");
         document.getElementById("next-list").setAttribute("disabled", "disabled");
    } else {
        document.getElementById("next").setAttribute("disabled", "disabled");
        document.getElementById("next-list").removeAttribute("disabled");
    }
}