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
    c = Math.random() * (6 - 1);
    for(i=0; i < c; i++) {
        let car = document.getElementById(cars[i]);
        car.style.display = "inline";
        s1=i;
    }
    document.getElementById("textarea").innerHTML="";
    if (c < 2)
        document.getElementById("solution").innerHTML = "car."
    else
        document.getElementById("solution").innerHTML = "cars."

    for(i=0; i < 5; i++) {
        document.getElementById(tvs[i]).style.display = "none";
    }

    
    shuffle(tvs);
    c = Math.random() * (6 - 1);
    for(i=0; i < c; i++) {
        let tv = document.getElementById(tvs[i]);
        tv.style.display = "inline";
        s2=i;
    }
    document.getElementById("textarea").innerHTML="";
    if (c < 2)
        document.getElementById("solution2").innerHTML = "tv."
    else
        document.getElementById("solution2").innerHTML = "tvs."
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
    console.log(solutions[s1])
    if (el.value == solutions[s1]) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
}

function solution2(el) {
    console.log(solutions[s2])
    if (el.value == solutions[s2]) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
}

$(function(){
    redo();
})