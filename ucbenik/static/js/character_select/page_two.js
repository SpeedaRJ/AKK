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
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, "d": d}
    });
}

function changeHairStyle(el, sex) {
    let svg = document.getElementById("character");
    let url = svg.data.split("/");
    const predict = (element) => element === "static";
    let index = url.findIndex(predict);
    let new_url = "";
    if (url[url.findIndex((element) => element === "short_hair" || element === "long_hair" || element === "bald" || element === "patch" || element === "bun.svg" || element === "curly.svg" || element === "long.svg" || element === "medium.svg")] === el.id) {
        console.log("Hairstyle already selected");
        return;
    }
    if (sex === "M") {
        for (let i = index; i < url.length; i++) {
            if (url[i] === "short_hair" || url[i] === "long_hair" || url[i] === "bald" || url[i] === "patch") {
                new_url += el.id + "/";
            } else {
                if (i === url.length - 1) {
                    new_url += url[i];
                } else {
                    new_url += url[i] + "/";
                }
            }
        }
    } else {
        for (let i = index; i < url.length; i++) {
            if (url[i] === "bun.svg" || url[i] === "curly.svg" || url[i] === "long.svg" || url[i] === "medium.svg") {
                new_url += el.id;
            } else {
                new_url += url[i] + "/";
            }
        }
    }
    svg.data = prepend + new_url;
    svg.addEventListener("load", function () {
        recolor();
    });
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
        console.log(type);
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

function changeGlasess(el,sex) {
    let svg = document.getElementById("character");
    let url = svg.data.split("/");
    let new_url="";
    let index = url.findIndex((element) => element ==="static");
    if (el.innerHTML === "Yes") {
        url[8] = "glasses";
    }else{
        url[8] = "no_glasses";
    }
    for (let i = index; i < url.length; i++) {
        if(i===url.length-1){
            new_url+=url[i];
        }else{
            new_url+=url[i]+"/";
        }
    }
    console.log(new_url);
    svg.data =prepend+new_url;
    svg.addEventListener("load",function () {
        recolor();
    },{once:true});
}
function changeSuite(el) {
    let svg = document.getElementById("character").contentDocument.children[0];
    if (el.id === "red_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style","fill:"+"rgb(145,44,70)");
        svg.querySelector("[id^=Hlace]").setAttribute("style","fill:"+"rgb(210,186,183)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"),function (e) {
            e.setAttribute("style","fill:"+"rgb(120,18,28)");
        });
    }
    else if (el.id === "blue_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style","fill:"+"rgb(0,84,166)");
        svg.querySelector("[id^=Hlace]").setAttribute("style","fill:"+"rgb(123,175,222)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"),function (e) {
            e.setAttribute("style","fill:"+"rgb(0,61,123)");
        });
    }
    else if (el.id === "green_suite") {
        svg.querySelector("[id^=Pulover]").setAttribute("style","fill:"+"rgb(0,168,129)");
        svg.querySelector("[id^=Hlace]").setAttribute("style","fill:"+"rgb(0,125,172)");
        [].forEach.call(svg.querySelectorAll("[id^=Gumb]"),function (e) {
            e.setAttribute("style","fill:"+"rgb(72,144,134)");
        });
    }
}
function translate(el) {
    let paras = document.getElementsByClassName("slo_name");
    if (el.target.value.toString().trim().toLowerCase() === "fat") {
        paras[0].innerHTML = "močnejše postave";
        let data = {
            "body_type": "fat"
        };
        update_session(data);
    } else if (el.target.value.toString().trim().toLowerCase() === "slim") {
        paras[0].innerHTML = "vitek";
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

});