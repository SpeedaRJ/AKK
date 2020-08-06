let solutions = [
    ["He has a beard"],
    ["She has glasses"],
    ["He has black hair"],
    ["She has short hair"],
    ["He has long hair"],
    ["She has curly hair"],
    ["He has a mustache"],
    ["She has straight hair"],
    ["He has grey hair"],
    ["She has orange hair"],
]

function redo() {
    var inputs = document.getElementsByClassName('textarea');
    for(var i=0; i<inputs.length;i++) 
        inputs[i].value="";
}

function solution(el,n) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solutions[n].join().toLowerCase()+'\\.*\\!*\\?*$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].parent.classList !== undefined && paras[x].parent.className.includes("correct") && !paras[x].parent.className.includes("incorrect"))
            counter++;
    }
    if(counter === solutions.length/2)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(function(){
    redo();
})