function solution(el,solutions) {
    let parent = el.parentElement;
    for (var i = 0; i < solutions.length; i++) {
        var solution = solutions[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution+'\.*\!*$')) {
            parent.classList.remove("incorrect");
            parent.classList.add("correct");
            break;
        } else {
            parent.classList.add("incorrect");
            parent.classList.remove("correct");
        }
    }
    let paras = document.getElementsByClassName("textarea");
    
    console.log(paras)
    if (!uniqueValue(paras)) {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
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

function uniqueValue(items) {
    for (var i=0; i < items.length; i++) {
        for (var j=0; j < items.length; j++) {
            if (i == j || items[i].value == "") continue;
            if(items[i].value.toLowerCase().trim().replace(/  +/g, ' ') == items[j].value.toLowerCase().trim().replace(/  +/g, ' '))
                return false;
        }
    }
    return true;
}