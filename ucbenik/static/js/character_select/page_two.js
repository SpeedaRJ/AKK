const prepend = "http://127.0.0.1:8000/";

const pSBC = (p, c0, c1, l) => {
    let r, g, b, P, f, t, h, i = parseInt, m = Math.round, a = typeof (c1) == "string";
    if (typeof (p) != "number" || p < -1 || p > 1 || typeof (c0) != "string" || (c0[0] != 'r' && c0[0] != '#') || (c1 && !a)) return null;
    if (!this.pSBCr) this.pSBCr = (d) => {
        let n = d.length, x = {};
        if (n > 9) {
            [r, g, b, a] = d = d.split(","), n = d.length;
            if (n < 3 || n > 4) return null;
            x.r = i(r[3] == "a" ? r.slice(5) : r.slice(4)), x.g = i(g), x.b = i(b), x.a = a ? parseFloat(a) : -1
        } else {
            if (n == 8 || n == 6 || n < 4) return null;
            if (n < 6) d = "#" + d[1] + d[1] + d[2] + d[2] + d[3] + d[3] + (n > 4 ? d[4] + d[4] : "");
            d = i(d.slice(1), 16);
            if (n == 9 || n == 5) x.r = d >> 24 & 255, x.g = d >> 16 & 255, x.b = d >> 8 & 255, x.a = m((d & 255) / 0.255) / 1000;
            else x.r = d >> 16, x.g = d >> 8 & 255, x.b = d & 255, x.a = -1
        }
        return x
    };
    h = c0.length > 9, h = a ? c1.length > 9 ? true : c1 == "c" ? !h : false : h, f = this.pSBCr(c0), P = p < 0, t = c1 && c1 != "c" ? this.pSBCr(c1) : P ? {
        r: 0,
        g: 0,
        b: 0,
        a: -1
    } : {
        r: 255,
        g: 255,
        b: 255,
        a: -1
    }, p = P ? p * -1 : p, P = 1 - p;
    if (!f || !t) return null;
    if (l) r = m(P * f.r + p * t.r), g = m(P * f.g + p * t.g), b = m(P * f.b + p * t.b);
    else r = m((P * f.r ** 2 + p * t.r ** 2) ** 0.5), g = m((P * f.g ** 2 + p * t.g ** 2) ** 0.5), b = m((P * f.b ** 2 + p * t.b ** 2) ** 0.5);
    a = f.a, t = t.a, f = a >= 0 || t >= 0, a = f ? a < 0 ? t : t < 0 ? a : a * P + t * p : 0;
    if (h) return "rgb" + (f ? "a(" : "(") + r + "," + g + "," + b + (f ? "," + m(a * 1000) / 1000 : "") + ")";
    else return "#" + (4294967296 + r * 16777216 + g * 65536 + b * 256 + (f ? m(a * 255) : 0)).toString(16).slice(1, f ? undefined : -2)
};

function changeSkinColor(e) {
    let svg = document.getElementById("character").contentDocument.children[0];
    [].forEach.call(svg.querySelectorAll(".cls-4"), function (el) {
        el.setAttribute("style", "fill:" + e.style.backgroundColor + ";");
    });
    [].forEach.call(svg.querySelectorAll(".cls-2"), function (el) {
        el.setAttribute("style", "fill:" + pSBC(0.15, e.style.backgroundColor) + ";");
    });
    let data = {
        "neck": pSBC(0.15, e.style.backgroundColor),
    };
    update_session(data);
    data = {
        "body_color": e.style.backgroundColor
    };
    update_session(data);
}

function update_session(d) {
    $.ajax({
        type: 'POST',
        url: "/update_session/" + Object.keys(d)[0],
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, "d": d},
        async:false
    });
}

function changeDress(el, color, type) {
    let svg = document.getElementById("character");
    let url = svg.data.split("/");
    let index = url.findIndex((element) => element === "static");
    let new_url = "";
    for (let i = index; i < url.length; i++) {
        if (url[i] === "dress" || url[i] === "shirt") {
            new_url += type + "/";
        } else {
            new_url += url[i] + "/";
        }
    }
    new_url = new_url.substring(0, new_url.length - 1);
    svg.data = prepend+new_url;
    svg.addEventListener("load",function () {
        recolor();
        let elemenet = document.getElementById("character").contentDocument.children[0];
        if (type ==="dress"){
            if(color==="blue"){
                [].forEach.call(elemenet.querySelectorAll("[id^=Obleka],[id^=cevlje]"),function (e) {
                    e.setAttribute("style","fill: #0474BB");
                });
            }else{
                [].forEach.call(elemenet.querySelectorAll("[id^=Obleka],[id^=cevlje]"),function (e) {
                    e.setAttribute("style","fill: #CD9246");
                });
            }
        }else{
            if(color==="red"){
                [].forEach.call(elemenet.querySelectorAll("[id^=Hlace],[id^=cevlje]"),function (e) {
                    e.setAttribute("style","fill: #074368");
                });
                [].forEach.call(elemenet.querySelectorAll("[id^=Majica]"),function (e) {
                    e.setAttribute("style","fill: #CC3333");
                });
            }else{
                [].forEach.call(elemenet.querySelectorAll("[id^=Hlace],[id^=cevlje]"),function (e) {
                    e.setAttribute("style","fill: #BBB7DC");
                });
                [].forEach.call(elemenet.querySelectorAll("[id^=Majica]"),function (e) {
                    e.setAttribute("style","fill: #D16E81");
                });
            }
        }
    },{once:true});
}

function changeBeard(el) {
    let svg = document.getElementById("character");
    let url = svg.data.split("/");
    const predict = (element) => element === "static";
    let index = url.findIndex(predict);
    let new_url = "";
    for (let i = index; i < url.length; i++) {
        if (url[i] === "full_beard.svg" || url[i] === "mustache.svg" || url[i] === "goatee.svg" || url[i] === "no_beard.svg") {
            new_url += el.id + ".svg";
        } else {
            new_url += url[i] + "/";
        }
    }
    svg.data = prepend + new_url;
    var type = el.id;
    svg.addEventListener("load", function (el) {
        recolor();
        let element = el.target.contentDocument.children[0];
        let colors = JSON.parse(document.getElementById("colors").textContent);
        [].forEach.call(element.querySelectorAll("[id=Brki]"), function (e) {
            e.setAttribute("style", "fill: " + colors['hair_color']);
        });
        if (type === "full_beard") {
            [].forEach.call(element.querySelectorAll("[id=Brada]"), function (e) {
                e.setAttribute("style", "fill: " + colors['hair_color']);
            });
        }

    }, {once: true});
}

function changeGlasess(el, sex) {
    let svg = document.getElementById("character");
    let url = svg.data.split("/");
    let new_url = "";
    let index = url.findIndex((element) => element === "static");
    if (el.innerHTML === "Yes") {
        url[8] = "glasses";
    } else {
        url[8] = "no_glasses";
    }
    for (let i = index; i < url.length; i++) {
        if (i === url.length - 1) {
            new_url += url[i];
        } else {
            new_url += url[i] + "/";
        }
    }
    svg.data = prepend + new_url;
    svg.addEventListener("load", function () {
        recolor();
    }, {once: true});
}

function translate(el) {
    let paras = document.getElementsByClassName("slo_name");
    if (el.target.value.toLowerCase().replace(/ +/g,"").match("^plump|fat$")) {
        paras[0].innerHTML = "močnejše postave";
        let data = {
            "body_type": "plump"
        };
        update_session(data);
    } else if (el.target.value.toString().trim().replace(/ +/g, '').toLowerCase().match("^slender|slim$")) {
        paras[0].innerHTML = "vitke postave";
        let data = {
            "body_type": "slim"
        };
        update_session(data);
    }
}

$(document).ready(function () {
    document.getElementById("name_input").addEventListener("input", function (e) {
        translate(e);
    });
    document.getElementById("name_input").addEventListener("foucusout",function (e) {
        if(e.target.value.toLowerCase().replace(/ +/g,"").match("^plump|fat$")){
            update_session({'body_type': "fat"})
        }else{
            update_session({'body_type': "slim"})
        }

    })
});