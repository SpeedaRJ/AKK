let solutions = {
    "policeman": ["policist"],
    "policewoman": ["policistka"],
    "pilot": ["pilot", "pilotka"],
    "engineer": ["inženir", "inženirka"],
    "doctor": ["zdravnik"],
    "photographer": ["fotograf", "fotografinja"],
    "postman": ["poštar"],
    "postwoman": ["poštarka"],
    "bus driver": ["voznik avtobusa", "voznica avtobusa"],
    "taxi driver": ["taksist", "taksistka"],
    "waiter": ["natakar"],
    "waitress": ["natakarica"],
    "plumber": ["vodovodar", "vodovodarka"],
    "farmer": ["kmet", "kmetica"],
    "musician": ["glasbenik", "glasbenica"],
    "cook": ["kuhar", "kuharica"],
    "businessman": ["poslovnež"],
    "businesswoman": ["poslovna ženska"],
    "firefighter": ["gasilec", "gasilka"],
    "teacher": ["učitelj", "učiteljica"],
    "lawyer": ["odvetnik", "odvetnica"],
    "judge": ["sodnik", "sodnica"],
    "writer": ["pisatelj", "pisateljica"],
    "poet": ["pesnik"],
    "poetess": ["pesnica"],
    "actor": ["igralec"],
    "actress": ["igralka"],
    "builder": ["gradbinec", "gradbinka"],
    "singer": ["pevec", "pevka"],
    "designer": ["oblikovalec", "oblikovalka"],
    "priest": ["duhovnik"],
    "librarian": ["knjižničar", "knjižničarka"],
    "salesman": ["prodajalec"],
    "saleswoman": ["prodajalka"]
}

let options = ["policeman", "policewoman", "pilot", "engineer", "doctor", "photographer", "postman", "postwoman", "bus driver", "taxi driver", "waiter", "waitress", "plumber", "farmer",
                "musician", "cook", "businessman", "businesswoman", "firefighter", "teacher", "lawyer", "judge", "writer", "poet", "poetess", "actor", "actress", "builder",
                "singer", "designer", "priest", "librarian", "salesman", "saleswoman"];

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
    if (solution.toLowerCase().split(",").includes(el.value.toLowerCase().trim().replace(/  +/g, ' ').replace(".", "").replace("!", ""))) {
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
    let work = document.getElementById("working-main1");
    let work2 = document.getElementById("working-main2");
    for(var i = 0; i < 10; i++) {
        var inx = Math.floor(Math.random() * 34);
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
            var obj = document.createElement("p");
            obj.innerHTML = job[i];
            div.appendChild(obj);
            work.insertBefore(div, work.firstChild);

            var input = document.getElementById(i.toString());
            input.setAttribute("onchange", `solution(this, \"${solutions[job[i]]}\")`)
            if(i == 0) {
                input.value = solutions[job[i]][0];
                input.classList.add("correct");
            }
        }
    }
}

$(document).ready(function() {
    setUp();
});