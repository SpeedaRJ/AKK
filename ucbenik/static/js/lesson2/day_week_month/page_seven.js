let objects1 = [
    "m01",
    "m02",
    "m03",
    "m04",
    "m05",
    "m06",
    "m07",
    "m08",
    "m09",
    "m10",
    "m11",
    "m12",
]


function redo(e) {
    for(i=0; i < objects1.length; i++) {
        try {
            var obj = document.getElementById(objects1[i]);
        } catch {
            continue
        }
        children = obj.children;
        children[0].classList.remove("incorrect");
        children[0].classList.remove("correct");
        children[1].classList.remove("incorrect");
        children[1].classList.remove("correct");
        if(Math.random()>0.5) {
            children[0].style.display="inline";
            children[1].style.display="none";
            children[1].classList.remove("empty");
        } else {
            children[0].style.display="none";
            children[1].style.display="inline";
        }
    }
}

function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.toLowerCase()+'\\.*\\!*$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    el.classList.remove("empty");
    if(document.getElementsByClassName('empty').length == 0 && document.getElementsByClassName('incorrect').length == 0)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}


$(function(){
    redo();
})