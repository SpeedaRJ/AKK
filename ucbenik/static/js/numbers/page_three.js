let cats = ["cat01",
            "cat02",
            "cat03",
            "cat04",
            "cat05",
            "cat06",
            "cat07",
            "cat08",
            "cat09",
            "cat10",
]

let solutions = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
]

let s = 0;
function redo(e) {
    shuffle(cats);
    for(i=0; i < 10; i++) {
        document.getElementById(cats[i]).style.display = "none";
    }
    c = Math.random() * (11 - 1);
    s = c;
    for(i=0; i < c; i++) {
        let cat = document.getElementById(cats[i]);
        cat.style.display = "inline";
    }
    document.getElementById("textarea").innerHTML="";
    console.log(c);
    if (c < 2)
        document.getElementById("solution").innerHTML = "cat."
    else
        document.getElementById("solution").innerHTML = "cats."
    document.getElementById("textarea").value="";
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
    if (el.value == solutions[s]) {
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