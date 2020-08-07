let cars = ["car01",
            "car02",
            "car03",
            "car04",
            "car05"
]

let tvs = ["tv01",
           "tv02",
           "tv03",
           "tv04",
           "tv05"
]


let solutions = [
    "one",
    "two",
    "three",
    "four",
    "five"
]

let s1 = 0;
let s2 = 0;
function redo(e) {
    for(i=0; i < 5; i++) {
        document.getElementById(cars[i]).style.display = "none";
    }
    c = Math.floor(Math.random() * (5)) + 1;
    for(i=0; i < c; i++) {
        let car = document.getElementById(cars[i]);
        car.style.display = "inline";
        s1=i;
    }
    if (c < 2)
        document.getElementById("solution").innerHTML = "car."
    else
        document.getElementById("solution").innerHTML = "cars."

    for(i=0; i < 5; i++) {
        document.getElementById(tvs[i]).style.display = "none";
    }
    document.getElementById("textarea").value="";

    
    shuffle(tvs);
    c = Math.floor(Math.random() * (5)) + 1;
    for(i=0; i < c; i++) {
        let tv = document.getElementById(tvs[i]);
        tv.style.display = "inline";
        s2=i;
    }
    if (c < 2)
        document.getElementById("solution2").innerHTML = "tv."
    else
        document.getElementById("solution2").innerHTML = "tvs."
    document.getElementById("textarea2").value="";
}

function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

function solution(el) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solutions[s1]+'\\.*\\!*$')) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    checkCorrectness()
}

function solution2(el) {
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solutions[s2]+'\\.*\\!*$')) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    checkCorrectness()
}

$(function(){
    redo();
})

function checkCorrectness() {
    let items = document.getElementsByClassName("textarea");
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}