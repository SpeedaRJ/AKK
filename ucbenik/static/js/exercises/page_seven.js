solutions1 = [
    ['(My name is Danielle)','(I am Danielle)'],
    ['I am 34 years old'],
    ['I live in Italy', 'I am from Italy']
]

solutions2 = [
    ['My name is Andrew','I am Andrew'],
    ['I am 71 years old'],
    ['I live in America', 'I am from America']
]

solutions3 = [
    ['My name is Sunita','I am Sunita'],
    ['I live in India', 'I am from India'],
    ['I am 89 years old']
]

solutions4 = [
    ['My name is Anita','I am Anita'],
    ['I live in Slovenia', 'I am from Slovenia','I live in Slovenija','I am from Slovenija'],
    ['I am 50 years old']
]

function solution1(el) {
    for (var i = 0; i < solutions1.length; i++) {
        var solution = solutions1[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.join('|').toLowerCase()+'\\.*\\!*$') != null && checkSiblings(el)) {
            el.classList.remove("incorrect");
            el.classList.add("correct");
            break;
        } else {
            el.classList.add("incorrect");
            el.classList.remove("correct");
        }
    }
    checkCorrectness();
}

function solution2(el) {
    for (var i = 0; i < solutions2.length; i++) {
        var solution = solutions2[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.join('|').toLowerCase()+'\\.*\\!*$') != null && checkSiblings(el)) {
            el.classList.remove("incorrect");
            el.classList.add("correct");
            break;
        } else {
            el.classList.add("incorrect");
            el.classList.remove("correct");
        }
    }
    checkCorrectness();
}

function solution3(el) {
    for (var i = 0; i < solutions3.length; i++) {
        var solution = solutions3[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.join('|').toLowerCase()+'\\.*\\!*$') != null && checkSiblings(el)) {
            el.classList.remove("incorrect");
            el.classList.add("correct");
            break;
        } else {
            el.classList.add("incorrect");
            el.classList.remove("correct");
        }
    }
    checkCorrectness();
}

function solution4(el) {
    for (var i = 0; i < solutions4.length; i++) {
        var solution = solutions4[i];
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^'+solution.join('|').toLowerCase()+'\\.*\\!*$') != null && checkSiblings(el)) {
            el.classList.remove("incorrect");
            el.classList.add("correct");
            break;
        } else {
            el.classList.add("incorrect");
            el.classList.remove("correct");
        }
    }
    checkCorrectness();
}

function checkSiblings(el) {
    var siblings = el.parentElement.children;
    for(var i = 0; i < siblings.length; i++) {
        if(el == siblings[i] || siblings[i].value == undefined)
            continue
        if (el.value.toLowerCase().trim().replace(/  +/g, ' ') == siblings[i].value.toLowerCase().trim().replace(/  +/g, ' '))
            return false
    }
    return true
}

function checkCorrectness() {
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 3)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}

$(function(){
    redo();
})

function redo(e) {
    var c = Math.floor(Math.random() * 3);
    var chars = document.getElementsByClassName('svg');
    var descriptions = document.getElementsByClassName('example');
    Array.from(chars).forEach((element) => {
        element.style.display="none";
    });
    Array.from(descriptions).forEach((element) => {
        element.style.display="none";
    });
    Array.from(document.getElementsByClassName('textarea')).forEach((element) => {
        element.value="";
        element.classList.remove("correct");
        element.classList.remove("incorrect");
    });
    document.getElementById("c"+c).style.display="block";
    document.getElementById("e"+c).style.display="block";
}
