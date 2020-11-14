let solutions = {
    "bed": ["I get up", "svg/lesson2/daily_routines/sun.svg"],
    "brush": ["I brush my teeth", "svg/lesson2/daily_routines/brush.svg"],
    "comb": ["I comb my hair", "svg/lesson2/daily_routines/hairbrush.svg"],
    "shirt": ["I get dressed", "svg/lesson2/daily_routines/shirt.svg"],
    "meal": ["i have breakfast/I have lunch/I have dinner", "svg/lesson2/daily_routines/meal.svg"],
    "newspaper": ["I read the newspaper", "svg/lesson2/daily_routines/newspaper.svg"],
    "car": ["I go to work/I arrive home", "svg/lesson2/daily_routines/car.svg"],
    "work": ["I work", "svg/lesson2/daily_routines/papers.svg"],
    "snack": ["I eat a snack", "svg/lesson2/daily_routines/apple.svg"],
    "cook": ["I make lunch", "svg/lesson2/daily_routines/pot.svg"],
    "dishes": ["I do the dishes", "svg/lesson2/daily_routines/dishes.svg"],
    "shower": ["I take a shower", "svg/lesson2/daily_routines/shower.svg"],
    "tv": ["I watch TV", "svg/lesson2/daily_routines/tv.svg"],
    "book": ["I read a book", "svg/lesson2/daily_routines/book.svg"],
    "night": ["I go to bed", "svg/lesson2/daily_routines/night.svg"]
}

let options = ["bed", "brush", "comb", "shirt", "meal", "newspaper", "car", "work", "snack", "dishes", "shower", "tv", "book", "night"];

let job = []

function redo() {
    let items = document.getElementsByClassName("textarea");
    for(let x = 0; x < items.length; x++){
        items[x].value = "";
        items[x].classList.remove("correct");
        items[x].classList.remove("incorrect");
    }
    document.getElementById("working-main").innerHTML = "";
    job = [];
    setUp();
}

function solution(el, solution) {
    if (solution.toLowerCase().split("/").includes(el.value.toLowerCase().trim().replace(/  +/g, ' '))) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    checkCorrectness()
}

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

function setUp(){
    let work = document.getElementById("working-main");
    for(var i = 0; i < 5; i++) {
        var inx = Math.floor(Math.random() * 14);
        if(!job.includes(solutions[options[inx]])){
            job.push(solutions[options[inx]]);
            i--;
            continue;
        }
        var div = document.createElement("div");
        div.classList.add("zaj");
        var obj = document.createElement("object");
        obj.classList.add("img-visual");
        obj.setAttribute("type", "image/svg+xml");
        obj.setAttribute("data", "/static/" + job[i][1])
        div.appendChild(obj);
        work.appendChild(div);

        var input = document.getElementById(i.toString());
        input.setAttribute("onchange", `solution(this, \"${job[i][0]}\")`)
        if(i == 0) {
            input.value = job[i][0].split("/")[0];
            input.classList.add("correct");
        }
    }
}

$(document).ready(function() {
    setUp();
});