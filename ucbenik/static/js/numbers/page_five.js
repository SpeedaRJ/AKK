let objects1 = [
    "obj1_01",
    "obj1_02",
    "obj1_03",
    "obj1_04",
    "obj1_05",
    "obj1_06",
    "obj1_07",
    "obj1_08",
    "obj1_09",
]

let objects2 = [
    "obj2_01",
    "obj2_02",
    "obj2_03",
    "obj2_04",
    "obj2_05",
    "obj2_06",
    "obj2_07",
    "obj2_08",
    "obj2_09",
    "obj2_10",
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
    "ten"
]

let s1 = 0;
let s2 = 0;
function redo(e) {
    shuffle(objects1);
    shuffle(objects2);
    //hide all objects
    for(i=0; i < objects1.length; i++) {
        document.getElementById(objects1[i]).style.display = "none";
    }
    for(i=0; i < objects2.length; i++) {
        document.getElementById(objects2[i]).style.display = "none";
    }

    c = Math.random() * (objects1.length);
    for(i=0; i < c; i++) {
        let car = document.getElementById(objects1[i]);
        car.style.display = "inline";
        s1=i;
    }
    document.getElementById("textarea").innerHTML="";
    if (c < 1)
        document.getElementById("solution").innerHTML = "house."
    else
        document.getElementById("solution").innerHTML = "houses."

    
    document.getElementById("textarea").value="";

    c = Math.random() * (objects2.length);
    for(i=0; i < c; i++) {
        let tv = document.getElementById(objects2[i]);
        tv.style.display = "inline";
        s2=i;
    }
    document.getElementById("textarea2").value="";
    if (c < 1)
        document.getElementById("solution2").innerHTML = "tree."
    else
        document.getElementById("solution2").innerHTML = "trees."
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