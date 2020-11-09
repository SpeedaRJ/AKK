var index = 0;
var lists = ["list-one","list-two","list-three","list-four","list-five"];

function changelist() {
     index++;
     if(index == 4){
        document.getElementById("next-list").setAttribute("disabled", "disabled");
        document.getElementById("next").removeAttribute("disabled");
     }
     document.getElementById(lists[index - 1]).setAttribute("hidden", "hidden");
     document.getElementById(lists[index]).removeAttribute("hidden");
}