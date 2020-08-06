function solution(el,solutions, gender, short=false) {
    if (short) {
        if (gender == "M") var gstring = "he's ";
        else var gstring = "she's ";
    }
    else {
        if (gender == "M") var gstring = "he is ";
        else var gstring = "she is ";
    }
    let parent = el.parentElement;
    for (var i = 0; i < solutions.length; i++) {
        var solution = solutions[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+gstring + solution+'\.*\!*$')) {
            parent.classList.remove("incorrect");
            parent.classList.add("correct");
            break;
        } else {
            parent.classList.add("incorrect");
            parent.classList.remove("correct");
        }
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x = 0; x < paras.length; x++) {
        if(paras[x].parentElement.classList !== undefined && paras[x].parentElement.className.includes("correct") && !paras[x].parentElement.className.includes("incorrect"))
            counter++;
    }
    if(counter === paras.length)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}