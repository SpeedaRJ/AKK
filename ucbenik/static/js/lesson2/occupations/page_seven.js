let solutions = {
    "policeman": ["policewoman"],
    "pilot": ["pilot"],
    "engineer": ["engineer"],
    "doctor": ["doctor"],
    "photographer": ["photographer"],
    "postman": ["postwoman"],
    "bus driver": ["bus driver"],
    "taxi driver": ["taxi driver"],
    "waiter": ["waitress"],
    "plumber": ["plumber"],
    "farmer": ["farmer"],
    "musician": ["musician"],
    "cook": ["cook"],
    "businessman": ["businesswoman"],
    "firefighter": ["firefighter"],
    "teacher": ["teacher"],
    "lawyer": ["lawyer"],
    "judge": ["judge"],
    "writer": ["writer"],
    "poet": ["poetess"],
    "actor": ["actress"],
    "builder": ["builder"],
    "singer": ["singer"],
    "designer": ["designer"],
    "librarian": ["librarian"],
    "salesman": ["saleswoman"]
}

let options = ["policeman", "pilot", "engineer", "doctor", "photographer", "postman", "bus driver", "taxi driver", "waiter", "plumber", "farmer",
                "musician", "cook", "businessman", "firefighter", "teacher", "lawyer", "judge", "writer", "poet", "actor","builder",
                "singer", "designer", "priest", "librarian", "salesman"];

let job = []

function redo() {
    let items = document.getElementsByClassName("textarea");
    for(let x = 0; x < items.length; x++){
        items[x].value = "";
        items[x].classList.remove("correct");
        items[x].classList.remove("incorrect");
    }
    items = document.getElementsByClassName("toDelete");
    var arr = [].slice.call(items);
    arr.forEach(function(x) {
        x.parentNode.removeChild(x);
    })
    job = [];
    setUp();
}

function solution(el, solution) {
    if (solution.toLowerCase().split("/").includes(el.value.toLowerCase().trim().replace(/  +/g, ' ').replace(".", "").replace("!", ""))) {
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
    let work2 = document.getElementById("working-main2");
    for(var i = 0; i < 10; i++) {
        var inx = Math.floor(Math.random() * 27);
        if(!job.includes(options[inx])){
            job.push(options[inx]);
            i--;
            continue;
        }
        if(i < 5){
            var div = document.createElement("div");
            div.classList.add("msg");
            div.classList.add("user");
            div.classList.add("full-width");
            div.classList.add("toDelete");
            var obj = document.createElement("p");
            obj.innerHTML = job[i];
            div.appendChild(obj);
            work.insertBefore(div, work.firstChild);

            var input = document.getElementById(i.toString());
            input.setAttribute("onchange", `solution(this, \"${solutions[job[i]]}\")`)
            if(i == 4) {
                input.value = solutions[job[i]][0];
                input.classList.add("correct");
            }
        } else {
            var div = document.createElement("div");
            div.classList.add("msg");
            div.classList.add("user");
            div.classList.add("full-width");
            div.classList.add("toDelete");
            var obj = document.createElement("p");
            obj.innerHTML = solutions[job[i]];
            div.appendChild(obj);
            work2.appendChild(div);

            var input = document.getElementById(i.toString());
            input.setAttribute("onchange", `solution(this, \"${job[i]}\")`)
        }
    }
}

$(document).ready(function() {
    setUp();
});