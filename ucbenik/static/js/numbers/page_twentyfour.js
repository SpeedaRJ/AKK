let numbers = [
    "zero",
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
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "twenty-one",
    "twenty-two",
    "twenty-three",
    "twenty-four",
    "twenty-five",
    "twenty-six",
    "twenty-seven",
    "twenty-eight",
    "twenty-nine",
    "thirty",
    "thirty-one",
    "thirty-two",
    "thirty-three",
    "thirty-four",
    "thirty-five",
    "thirty-six",
    "thirty-seven",
    "thirty-eight",
    "thirty-nine",
    "forty",
    "forty-one",
    "forty-two",
    "forty-three",
    "forty-four",
    "forty-five",
    "forty-six",
    "forty-seven",
    "forty-eight",
    "forty-nine",
    "fifty",
    "fifty-one",
    "fifty-two",
    "fifty-three",
    "fifty-four",
    "fifty-five",
    "fifty-six",
    "fifty-seven",
    "fifty-eight",
    "fifty-nine",
    "sixty",
    "sixty-one",
    "sixty-two",
    "sixty-three",
    "sixty-four",
    "sixty-five",
    "sixty-six",
    "sixty-seven",
    "sixty-eight",
    "sixty-nine",
    "seventy",
    "seventy-one",
    "seventy-two",
    "seventy-three",
    "seventy-four",
    "seventy-five",
    "seventy-six",
    "seventy-seven",
    "seventy-eight",
    "seventy-nine",
    "eighty",
    "eighty-one",
    "eighty-two",
    "eighty-three",
    "eighty-four",
    "eighty-five",
    "eighty-six",
    "eighty-seven",
    "eighty-eight",
    "eighty-nine",
    "ninety",
    "ninety-one",
    "ninety-two",
    "ninety-three",
    "ninety-four",
    "ninety-five",
    "ninety-six",
    "ninety-seven",
    "ninety-eight",
    "ninety-nine",
    "one hundred"
]
function redo(e) {
    let table = document.getElementById("help-table");
    table.innerHTML="";
    for(i=0; i < 5; i++) {
        var n = Math.round(Math.random() * 100);
        let word = numbers[n];
        let html = '<div class="help row"><button class="col-lg-6 tip" disabled id="num'+n+'"><p>'+n+
        '</p><input class="textarea" size="5" onchange="solution(this,'+n+
        ')"/></button><button class="col-lg-6 tip c2" id="word'+n+'"><p>'+word+
        '</p><input class="textarea" size="5" onchange="solution(this,'+"'"+word+"'"+
        ')"/></button></div>';
        table.innerHTML+=html;
        let item1 = document.getElementById("num"+n);
        let item2 = document.getElementById("word"+n);
        if(Math.random()>0.5) {
            item1.children[0].style.display="none";
            item1.children[1].style.display="inline";
            item2.children[0].style.display="inline";
            item2.children[1].style.display="none";
        } else {
            item1.children[1].style.display="none";
            item1.children[0].style.display="inline";
            item2.children[1].style.display="inline";
            item2.children[0].style.display="none";
        }
    }
}

function solution(el,solution) {
    let parent = el.parentElement;
    if (el.value.replace('fourty','forty') == solution) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("tip")
    let counter = 0;
    for(let x in paras) {
        if(paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 5)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}


$(function(){
    redo();
})