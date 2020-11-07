function next(el) {
    document.getElementById("instructions").innerHTML="Kot vidiš, pri prvi osebi, obliki I AM "+
                                                          "odvzamemo A in dobimo skrajšano obliko "+
                                                          "I'M.  Tudi glagolu ARE odvzamemo A in tako "+
                                                          "dobimo oblike: YOU'RE, WE'RE, THEY'RE. "+
                                                          "Glagolu IS pa odvzamemo I in dobimo "+
                                                          "oblike: HE'S, SHE'S in IT'S. Če želiš slišati "+
                                                          "različne izgovorjave – dolgih in kratkih "+
                                                          "oblik – klikni na besede v tabeli."
    document.getElementById("next").removeAttribute("disabled");
    el.style.display="none";
}