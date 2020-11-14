
let solutions = {'He/She extinguishes fires.': 'firefighter',
    'He/She works in the fashion industry.': 'designer', 'The result of his/her work is a book.': 'writer',
    'The result of his/her work is poetry.': 'poet/poetess', 'He/She gives live performances.': 'singer/musician',
    'He/She can be seen on TV or on stage.': 'actor/actress', 'He/She works at the cashier.': 'salesman/saleswoman',
    'He/She builds houses.': 'builder', 'He/She is often seen in front of the black board.': 'teacher',
    'He/She drives a cab.': 'taxi driver', 'He/She is surrounded by books.': 'librarian',
    'He/She decides whether a person is guilty or not.': 'judge', 'He/She serves drinks.': 'waiter/waitress',
    'He/She prepares meals.': 'cook', 'He/She brings you mail.': 'postman/postwoman',
    'He/She tells you what medicine you should take.': 'doctor', 'He/She takes your photograph.': 'photographer', 'He/She drives children to school.': 'bus driver',
    'He/She can fly a plane.': 'pilot', 'He/She has a gun and handcuffs.': 'policeman/policewoman'};

let options = ['He/She extinguishes fires.', 'He/She works in the fashion industry.', 'The result of his/her work is a book.', 'The result of his/her work is poetry.', 'He/She gives live performances.', 'He/She can be seen on TV or on stage.', 'He/She works at the cashier.', 'He/She builds houses.', 'He/She is often seen in front of the black board.', 'He/She drives a cab.', 'He/She is surrounded by books.', 'He/She decides whether a person is guilty or not.', 'He/She serves drinks.', 'He/She prepares meals.', 'He/She brings you mail.', 'He/She tells you what medicine you should take.', 'He/She takes your photograph.', 'He/She drives children to school.', 'He/She can fly a plane.', 'He/She has a gun and handcuffs.'];

let job = [];

function redo() {
    let items = document.getElementsByClassName("textarea");
    for (let x = 0; x < items.length; x++) {
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
    for (let x = 0; x < items.length; x++) {
        if (items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
        document.getElementById("next").setAttribute("disabled", "disabled");
    }
}

function setUp() {
    let work = document.getElementById("working-main");
    for (var i = 0; i < 5; i++) {
        var inx = Math.floor(Math.random() * 14);
        if (!job.includes(options[inx])) {
            job.push(options[inx]);
            i--;
            continue;
        }

        const input = document.getElementById(i.toString());
        input.setAttribute("onchange", `solution(this, \"${solutions[job[i]]}\")`);
        if (i == 0) {
            input.value = solutions[job[i]].split("/")[0];
            input.classList.add("correct");
        }
    }
}

$(document).ready(function () {
    setUp();
});