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
    document.getElementById("working-main").innerHTML = "";
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
    for(var i = 0; i < 5; i++) {
        var inx = Math.floor(Math.random() * 27);
        if(!job.includes(options[inx])){
            job.push(options[inx]);
            i--;
            continue;
        }
        var div = document.createElement("div");
        div.classList.add("msg");
        div.classList.add("user");
        div.classList.add("full-width");
        var obj = document.createElement("p");
        obj.innerHTML = job[i];
        div.appendChild(obj);
        work.appendChild(div);

        var input = document.getElementById(i.toString());
        input.setAttribute("onchange", `solution(this, \"${solutions[job[i]]}\")`)
        if(i == 0) {
            input.value = solutions[job[i]][0];
            input.classList.add("correct");
        }
    }
}

$(document).ready(function() {
    setUp();
});