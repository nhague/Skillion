! function(e, t) {
    "function" == typeof define && define.amd ? define(t) : "object" == typeof exports ? module.exports = t() :
        e.ResizeSensor = t()
}(this, function() {
    function e(e, t) {
        var i = Object.prototype.toString.call(e),
            n = "[object Array]" === i || "[object NodeList]" === i || "[object HTMLCollection]" === i ||
            "[object Object]" === i || "undefined" != typeof jQuery && e instanceof jQuery || "undefined" !=
            typeof Elements && e instanceof Elements,
            o = 0,
            s = e.length;
        if (n)
            for (; s > o; o++) t(e[o]);
        else t(e)
    }
    if ("undefined" == typeof window) return null;
    var t = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame ||
        function(e) {
            return window.setTimeout(e, 20)
        },
        i = function(n, o) {
            function s() {
                var e = [];
                this.add = function(t) {
                    e.push(t)
                };
                var t, i;
                this.call = function() {
                    for (t = 0, i = e.length; i > t; t++) e[t].call()
                }, this.remove = function(n) {
                    var o = [];
                    for (t = 0, i = e.length; i > t; t++) e[t] !== n && o.push(e[t]);
                    e = o
                }, this.length = function() {
                    return e.length
                }
            }

            function a(e, t) {
                return e.currentStyle ? e.currentStyle[t] : window.getComputedStyle ? window.getComputedStyle(
                    e, null).getPropertyValue(t) : e.style[t]
            }

            function r(e, i) {
                if (e.resizedAttached) return void e.resizedAttached.add(i);
                e.resizedAttached = new s, e.resizedAttached.add(i), e.resizeSensor = document.createElement(
                    "div"), e.resizeSensor.className = "resize-sensor";
                var n =
                    "position: absolute; left: 0; top: 0; right: 0; bottom: 0; overflow: hidden; z-index: -1; visibility: hidden;",
                    o = "position: absolute; left: 0; top: 0; transition: 0s;";
                e.resizeSensor.style.cssText = n, e.resizeSensor.innerHTML =
                    '<div class="resize-sensor-expand" style="' + n + '"><div style="' + o +
                    '"></div></div><div class="resize-sensor-shrink" style="' + n + '"><div style="' + o +
                    ' width: 200%; height: 200%"></div></div>', e.appendChild(e.resizeSensor), "static" ==
                    a(e, "position") && (e.style.position = "relative");
                var r, c, l, p, d = e.resizeSensor.childNodes[0],
                    u = d.childNodes[0],
                    h = e.resizeSensor.childNodes[1],
                    f = e.offsetWidth,
                    m = e.offsetHeight,
                    g = function() {
                        u.style.width = "100000px", u.style.height = "100000px", d.scrollLeft = 1e5, d.scrollTop =
                            1e5, h.scrollLeft = 1e5, h.scrollTop = 1e5
                    };
                g();
                var y = function() {
                        c = 0, r && (f = l, m = p, e.resizedAttached && e.resizedAttached.call())
                    },
                    z = function() {
                        l = e.offsetWidth, p = e.offsetHeight, r = l != f || p != m, r && !c && (c = t(y)),
                            g()
                    },
                    _ = function(e, t, i) {
                        e.attachEvent ? e.attachEvent("on" + t, i) : e.addEventListener(t, i)
                    };
                _(d, "scroll", z), _(h, "scroll", z)
            }
            e(n, function(e) {
                r(e, o)
            }), this.detach = function(e) {
                i.detach(n, e)
            }
        };
    return i.detach = function(t, i) {
        e(t, function(e) {
            e.resizedAttached && "function" == typeof i && (e.resizedAttached.remove(i), e.resizedAttached
                .length()) || e.resizeSensor && (e.contains(e.resizeSensor) && e.removeChild(
                e.resizeSensor), delete e.resizeSensor, delete e.resizedAttached)
        })
    }, i
}),
function(e, t, i) {
    "use strict";
    if (e.console === i && (e.console = {}, e.console.log = function() {}), t === i) return void console.log(
        "zipMoney JS Library requires jQuery");
    if (e.ZIPMONEYLOADED) return void console.log("zipMoney JS Library is already Loaded.");
    if (t.zepto !== i) console.log("Loaded zipMoney Widget JS. Using Zepto Js");
    else {
        if (t.fn.jquery < 1.7) return void console.log("zipMoney JS Library requires at least jQuery 1.7 ");
        console.log("Loaded zipMoney Widget JS. The jQuery version is " + t.fn.jquery)
    }
    e.ZIPMONEYLOADED = !0;
    var n = function() {};
    n.prototype = {
        options: {
            widgets: [],
            assets: {},
            popupGroup: [],
            assetsCache: []
        },
        _allowedAttributes: ["zm-asset", "zm-widget", "zm-asset-file"],
        _widgetAttributeAssetKey: "zm-asset",
        _widgetAttributeType: "zm-widget",
        _widgets: [],
        _rootEl: null,
        _merchantId: null,
        _environment: ["dev", "sandbox", "production"],
        _apiEndpoint: {
            dev: "http://api.dev1.zipmoney.com.au/v1/",
            sandbox: "https://api.sandbox.zipmoney.com.au/v1/",
            production: "https://api.zipmoney.com.au/v1/"
        },
        _iframeLib: {
            dev: "https://account.dev1.zipmoney.com.au/scripts/iframe/zipmoney-checkout.js",
            sandbox: "https://account.sandbox.zipmoney.com.au/scripts/iframe/zipmoney-checkout.js",
            production: "https://account.zipmoney.com.au/scripts/iframe/zipmoney-checkout.js"
        },
        _apiEndpointUrl: null,
        _iframeLibUrl: null,
        _zipMoneyCheckout: null,
        _init: function(e, i) {
            this.options = t.extend({}, this.options, e);
            var n = this;
            this._rootEl = i, n._ready(n)
        },
        registerWidget: function(e, i, n) {
            this._widgets.push({
                "class": e,
                name: i,
                attributes: n
            });
            var o = this;
            t.each(n, function(e, t) {
                o._allowedAttributes.push(t)
            })
        },
        _ready: function(e) {
            var n, o = t(e._rootEl),
                s = t("[zm-merchant] , [data-zm-merchant]"),
                a = t("[zm-asset-path] , [data-zm-asset-path]");
            try {
                if (o.length) e._merchantId = o.attr("merchant");
                else if (s && s.length) e._merchantId = s.attr("zm-merchant"), e._merchantId || (e._merchantId =
                    s.attr("data-zm-merchant")), o = s;
                else if (a && a.length) {
                    var r = a.attr("zm-asset-path");
                    r || (r = a.attr("data-zm-asset-path")), o = a, n = t.get(r, function(t) {
                        e._assets = t.assets, e._assetValues = t.asset_values
                    })
                } else console.log("zipMoney Merchant Id not provided");
                if (e._merchantId) {
                    var c = o.attr("env");
                    c || (c = o.attr("data-env"));
                    var l = e._apiEndpoint.dev,
                        p = e._iframeLib.dev;
                    c && t.inArray(c, e._environment) >= 0 && (l = e._apiEndpoint[c], p = e._iframeLib[
                        c]), e._apiEndpointUrl = l, t.getScript(p, function() {
                        e._zipMoneyCheckout = zipMoney
                    }), n = t.ajax({
                        url: l + "assets?merchantid=" + e._merchantId,
                        jsonp: "callback",
                        dataType: "jsonp",
                        success: function(t) {
                            e._assets = t.assets, e._assetValues = t.asset_values, e._settings =
                                t.settings
                        }
                    })
                }
                n !== i ? n.done(function() {
                    e._collectWidgetsEl(e)
                }) : console.log("Cannot load the assets")
            } catch (d) {
                console.log(d)
            }
        },
        _collectWidgetsEl: function(e) {
            e._widgetElList = t("[" + e._widgetAttributeType + "],[data-" + e._widgetAttributeType +
                "]"), e._widgetElList.each(function(t, i) {
                e._createWidget(i, e)
            })
        },
        _createWidget: function(e, n) {
            var o, s, a;
            s = t(e).attr(n._widgetAttributeType), s || (s = t(e).attr("data-" + n._widgetAttributeType)),
                s === i && console.log("ZipMoney Widget type is not defined");
            var r, c = n._getWidgetClass(s);
            o = {};
            for (var l = 0; l < n._allowedAttributes.length; l++) r = t(e).attr(n._allowedAttributes[
                l]), r || (r = t(e).attr("data-" + n._allowedAttributes[l])), r !== i && (o[n._allowedAttributes[
                    l].replace(new RegExp("zm-", "g"), "").replace(new RegExp("-", "g"), "_")] =
                r);
            a = new c["class"](o, e, n), a._render()
        },
        _getWidgetClass: function(e) {
            var i;
            return t.each(this._widgets, function(t, n) {
                n.name === e && (i = n)
            }), i
        },
        addPopupToGroup: function(e) {
            e.type = "iframe", this.options.popupGroup.push(e)
        },
        _getAsset: function(e) {
            var i, n = [],
                o = this,
                s = 0;
            return (i = this._getAssetFromCache(e)) ? i : (t.each(this._assets, function(t, i) {
                i.type === e && (n[s] = i, s++)
            }), s = 0, n = n.sort(function(e, t) {
                return e.sequence - t.sequence
            }), t.each(n, function(e, t) {
                switch (t.content_type) {
                    case "html":
                        n[e] = o._processHtml(t);
                        break;
                    case "text":
                        n[e] = o._processText(t);
                        break;
                    case "image":
                        n[e] = o._processImage(t)
                }
            }), this.options.assetsCache[e] = n, n)
        },
        _getAssetFromCache: function(e) {
            return this.options.assetsCache[e] !== i ? this.options.assetsCache[e] : !1
        },
        _processImage: function(e) {
            var t = '<img src="' + e.url.replace(new RegExp("http:", "g"), "") + '">';
            return e.value = t, e.is_promise = !1, e
        },
        _processHtml: function(e) {
            var i = this;
            return e.is_promise = !1, e.url && (e.promise = t.get(e.url.replace(new RegExp("http:",
                "g"), "")).then(function(n) {
                return t.each(i._getReplaceValues(e.asset_values), function(e, t) {
                    t.key && t.value && (n = n.replace(new RegExp(t.key, "g"), t.value),
                        n = n.replace(new RegExp("http:", "g"), ""))
                }), e.value = n, e
            }), e.is_promise = !0), e
        },
        _processText: function(e) {
            var i = this;
            return e.value && t.each(i._getReplaceValues(e.asset_values), function(t, i) {
                i.key && i.value && (e.value = e.value.replace(i.key, i.value))
            }), e.is_promise = !1, e
        },
        _getReplaceValues: function(e) {
            var n, o, s, a;
            return e && t.isArray(e) || (e = []), this._assetValues && t.isArray(this._assetValues) ||
                (this._assetValues = []), !e || e === i || e.length <= 0 ? n = this._assetValues : (s = [],
                    a = 0, t.each(e, function(e, i) {
                        o = !1, t.each(this._assetValues, function(e, n) {
                            i.key === n.key && (this._assetValues[e] = t.merge(n, i), o = !
                                0, a++)
                        }), o && (s[a] = i)
                    }), n = t.merge(this._assetValues, s)), n
        },
        _renderInIframe: function(e, i) {
            var n = t("<iframe>", {
                frameborder: 0,
                scrolling: "no",
                width: "100%",
                id: "zipif",
                height: "auto"
            });
            const o = function() {
                var e = t(n).contents().find("body").css("height");
                e && t(n).height(e)
            };
            return n.load(function() {
                t(this).contents().find("body").attr({
                    height: "auto !important;"
                }).append(e);
                setTimeout(function() {
                    o()
                }, 100)
            }), i.append(n), t(n).contents().find("img,script,style").on("load", n, function() {
                o()
            }), new ResizeSensor(t(n).contents().find("body"), function() {
                o()
            }), n
        },
        setup: function(e, t) {
            this._init(e, t)
        }
    }, e.$zmJs = new n, t(function() {
        e.$zmJs.setup({}, "zipmoney")
    })
}(window, window.jQuery),
function(e, t, i) {
    "use strict";
    var n = function(e, n, o) {
        this.options = e, this.superObj = o, this.el = n, this._render = function() {
            try {
                var e =
                    "https://d3k1w8lx8mqizo.cloudfront.net/INTEGRATIONS/2016/zippay/logos/zippay-grey-black.png",
                    n = "",
                    o = "zipPay",
                    s = "Buy Now, <strong>Pay Later</strong>";
                this.superObj._settings && this.superObj._settings.product_classification && (o =
                        this.superObj._settings.product_classification, "zipmoney" === o.toLowerCase() &&
                        (e = "https://d3k1w8lx8mqizo.cloudfront.net/logo/90px/zipMoney.png")), this.options
                    .logo !== i && (e = this.options.logo), this.options.tagline !== i && (s = this.options
                        .tagline), t(this.el).removeAttr("data-zm-widget"), t(this.el).removeAttr(
                        "data-zm-popup-asset"), t(this.el).removeAttr("data-zm-amount"), t(this.el).removeAttr(
                        "zm-widget"), t(this.el).removeAttr("zm-popup-asset"), t(this.el).removeAttr(
                        "zm-amount"), t(this.el).addClass("zip_tagline"), t(this.el).attr(
                        "data-zm-widget", "popup"), t(this.el).attr("data-zm-popup-asset",
                        "termsdialog"), e && (n = "<img src='" + e +
                        "' height='16' style='vertical-align:text-bottom;height:16px !important' alt='" +
                        o + "'>");
                var a = "<span class='zip_tagline_text'>" + s + " </span>" + n,
                    r = /learn more/i,
                    c = /more/i,
                    l = /more info/i;
                !(r.test(t(this.el).next().text()) || c.test(t(this.el).next().text()) || l.test(t(
                    this.el).next().text())) || "popup" !== t(this.el).next().attr("zm-widget") &&
                    "popup" !== t(this.el).next().attr("data-zm-widget") || (this.options.info =
                        "true", t(this.el).next().remove()), this.options.info !== i && "true" ===
                    this.options.info && (a +=
                        " <a class='zip-info' style='font-size:10px;display:inline !important;cursor:pointer'>more info &raquo;</a>"
                    ), a +=
                    "<script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');ga('create', 'UA-46330661-10', 'auto');ga('send', 'pageview');</script>";
                var p = t(this.el).append(a);
                this.superObj._createWidget(t(this.el), this.superObj), t(this.el).on("click",
                        function() {
                            ga("send", "event", "learn-more-query", "click", "Learn More")
                        }), t(this.el).css("display", "inline"), this.options.info !== i && "true" ===
                    this.options.info && p.children(".zip-info").css("display", "inline")
            } catch (d) {
                console.log(d)
            }
        }
    };
    e.$zmJs !== i && e.$zmJs.registerWidget(n, "repaycalc", ["zm-min-monthly-payment", "zm-amount", "zm-logo",
        "zm-info", "zm-tagline"
    ])
}(window, window.jQuery),
function(e, t, i) {
    "use strict";
    var n = function(e, i, n) {
        this.options = e, this.superObj = n, this.el = i, this._render = function() {
            try {
                var e, i = this.superObj._getAsset(this.options.asset),
                    n = this;
                t.each(i, function(i, o) {
                    o.is_promise ? o.promise.done(function() {
                        "html" === o.content_type && "false" !== n.options.iframe ? (
                            e = n.superObj._renderInIframe(o.value, t(n.el)), n.bindApp(
                                e)) : t(n.el).append(o.value)
                    }) : "html" === o.content_type && "false" !== n.options.iframe ? (e =
                        n.superObj._renderInIframe(o.value, t(n.el)), n.bindApp(e)) : t(n
                        .el).append(o.value)
                })
            } catch (o) {
                console.log(o)
            }
        }, this.bindApp = function(e) {
            var i = this;
            e.contents().find("body a.button").click(function(e) {
                "false" !== t(this).data("iframe") && (i.superObj._zipMoneyCheckout.checkout(
                    this.href), e.preventDefault())
            })
        }
    };
    e.$zmJs !== i && e.$zmJs.registerWidget(n, "inline", ["zm-iframe"])
}(window, window.jQuery),
function(e, t, i) {
    "use strict";
    if (t === i) return void console.log("zipMoney Popup widget requires jQuery");
    if (!(t.fn.jquery < 1.7)) {
        t("<link>").appendTo("head").attr({
            type: "text/css",
            rel: "stylesheet"
        }).attr("href", "//d3k1w8lx8mqizo.cloudfront.net/lib/js/fancybox/dist/css/jquery.fancybox.css");
        var n, o;
        t.fancybox && (n = t.extend(!0, t.fancybox, {})), t.fn.fancybox && (o = t.extend(!0, t.fn.fancybox, {}));
        var s = function() {
            var e, s;
            t.fn.zipModal = t.extend(!0, t.fn.fancybox, {}), t.zipModal = t.extend(!0, t.fancybox, {}), o &&
                (t.fn.fancybox = t.extend(!0, o, {})), n && (t.fancybox = t.extend(!0, n, {})), t.zipModal !==
                i ? (e = t.zipModal, s = document.createTouch !== i, console.log("Fancybox Version:- " +
                    e.version)) : console.log("Zipmoney Widgets:- Fancybox is not defined"), t.zipModal =
                t.extend(!0, e, {
                    _loadIframeFancy: function() {
                        this._loadIframe()
                    },
                    _loadIframe: function() {
                        var i = e.coming,
                            n = t(i.tpl.iframe.replace(/\{rnd\}/g, (new Date).getTime())).attr(
                                "scrolling", s ? "auto" : i.iframe.scrolling);
                        "zipmoney-widgets-fancybox" !== i.wrapCSS && n.attr("src", i.href), t(i.wrap)
                            .bind("onReset", function() {
                                try {
                                    t(this).find("iframe").hide().attr("src", "//about:blank")
                                        .end().empty()
                                } catch (e) {}
                            }), i.iframe.preload && (e.showLoading(), n.one("load", function() {
                                t(this).attr("data-ready", 1), i.content = t(this),
                                    "zipmoney-widgets-fancybox" === i.wrapCSS && (t(this)
                                        .contents().find("body").html(t(i.href).contents()
                                            .find("body").html()), t(i.href).hide()), s ||
                                    t(this).bind("load.fb", e.update), t(this).parents(
                                        ".fancybox-wrap").width("100%").removeClass(
                                        "fancybox-tmp").show(), e._afterLoad()
                            })), i.content = n.appendTo(i.inner), i.iframe.preload || e._afterLoad()
                    }
                })
        };
        t.fancybox === i || "2.1.5" !== t.fancybox.version ? (console.log("Loading fancybox from our CDN."),
            t.getScript("//d3k1w8lx8mqizo.cloudfront.net/lib/js/fancybox/dist/js/jquery.fancybox.pack.js",
                s)) : (console.log("Skipping fancybox loading. Fancybox already loaded."), s());
        var a = function(e, n, o) {
            this.options = e, this.superObj = o, this.el = n, this.popupGroup = [], this.addPopupToGroup =
                function(e) {
                    e.type = "iframe", this.popupGroup.push(e)
                }, this._render = function() {
                    try {
                        var e, i = this.superObj._getAsset(this.options.asset),
                            n = this.superObj._getAsset(this.options.popup_asset),
                            o = this;
                        t.each(i, function(i, n) {
                            n.is_promise ? n.promise.done(function() {
                                    "html" === n.content_type && "false" !== o.options.iframe ?
                                        (e = o.superObj._renderInIframe(n.value, t(o.el)), e.contents()
                                            .find("body").on("click", function() {
                                                o._fancybox(o)
                                            })) : t(o.el).append(n.value)
                                }) : "html" === n.content_type && "false" !== o.options.iframe ?
                                (e = o.superObj._renderInIframe(n.value, t(o.el)), e.contents().find(
                                    "body").on("click", function() {
                                    o._fancybox(o)
                                })) : t(o.el).append(n.value)
                        });
                        var s, a;
                        t.each(n, function(e, i) {
                            i.is_promise && i.promise.done(function() {
                                a = o.options.popup_asset + "-" + e, s = t("#" + a), s.length ||
                                    (s = t("<iframe>", {
                                        frameborder: 0,
                                        scrolling: "no",
                                        width: "100%",
                                        height: "auto"
                                    }), s.attr("id", a), s.load(function() {
                                        t(this).contents().find("body").append(i.value);
                                        var e = t(this).contents().find("body").outerHeight(),
                                            n = t(this).contents().find("body").outerWidth();
                                        t(this).width(n), t(this).height(e)
                                    }), s.hide(), t("body").append(s)), i.childEl = s, i.childId =
                                    a, o.addPopupToGroup({
                                        href: "#" + a,
                                        autoSize: !0,
                                        autoResize: !0,
                                        fitToView: !0,
                                        wrapCSS: "zipmoney-widgets-fancybox",
                                        childEl: s,
                                        asset: i
                                    })
                            })
                        }), t(o.el).css("display", "block"), t(o.el).click(function() {
                            o._fancybox(o)
                        })
                    } catch (r) {
                        console.log(r)
                    }
                }, this._fancybox = function(e) {
                    t.zipModal !== i ? (console.log("Rendering fancybox using fancybox version:- " + t.zipModal
                        .version), t.zipModal(e.popupGroup)) : console.log(
                        "Zipmoney Widgets:- Fancybox is not defined")
                }
        };
        e.$zmJs !== i && e.$zmJs.registerWidget(a, "popup", ["zm-popup-asset"])
    }
}(window, window.jQuery),
function(e, t, i) {
    "use strict";
    var n = function(e, n, o) {
        this.options = e, this.superObj = o, this.el = n, this._render = function() {
            try {
                var e =
                    "https://d3k1w8lx8mqizo.cloudfront.net/INTEGRATIONS/2016/zippay/logos/zippay-grey-black.png",
                    n = "",
                    o = "zipPay",
                    s = "Buy Now, <strong>Pay Later</strong>";
                this.superObj._settings && this.superObj._settings.product_classification && (o =
                        this.superObj._settings.product_classification, "zipmoney" === o.toLowerCase() &&
                        (e =
                            "https://s3-ap-southeast-2.amazonaws.com/cdn.production/logo/90px/zipMoney.png"
                        )), this.options.logo !== i && (e = this.options.logo), this.options.tagline !==
                    i && (s = this.options.tagline), t(this.el).removeAttr("data-zm-widget"), t(this.el)
                    .removeAttr("data-zm-popup-asset"), t(this.el).removeAttr("data-zm-amount"), t(
                        this.el).removeAttr("zm-widget"), t(this.el).removeAttr("zm-popup-asset"), t(
                        this.el).removeAttr("zm-amount"), t(this.el).addClass("zip_tagline"), t(this.el)
                    .attr("data-zm-widget", "popup"), t(this.el).attr("data-zm-popup-asset",
                        "termsdialog"), e && (n = "<img src='" + e +
                        "' height='16' style='vertical-align:text-bottom;height:16px !important' alt='" +
                        o + "'>");
                var a = "<span class='zip_tagline_text'>" + s + " </span>" + n;
                this.options.info !== i && "true" === this.options.info && (a +=
                        " <a class='zip-info' style='font-size:10px;display:inline !important;cursor:pointer'>more info &raquo;</a>"
                    ), a +=
                    "<script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');ga('create', 'UA-46330661-10', 'auto');ga('send', 'pageview');</script>";
                var r = t(this.el).append(a);
                this.superObj._createWidget(t(this.el), this.superObj), t(this.el).on("click",
                        function() {
                            ga("send", "event", "learn-more-query", "click", "Learn More")
                        }), t(this.el).css("display", "inline"), this.options.info !== i && "true" ===
                    this.options.info && r.children(".zip-info").css("display", "inline")
            } catch (c) {
                console.log(c)
            }
        }
    };
    e.$zmJs !== i && e.$zmJs.registerWidget(n, "tagline", ["zm-logo", "zm-info", "zm-tagline"])
}(window, window.jQuery);
