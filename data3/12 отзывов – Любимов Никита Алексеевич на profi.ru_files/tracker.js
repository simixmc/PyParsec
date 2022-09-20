;(function(d, w, nav, sc) {
  function serialize(obj) {
    return Object.keys(obj)
      .map(function(key) {
        return [key, obj[key]].join('=')
      })
      .join('&')
  }

  function getCookie(name) {
    var matches = d.cookie.match(
      new RegExp('(?:^|; )' + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)')
    )
    return matches ? decodeURIComponent(matches[1]) : ''
  }

  function getWGL() {
    var canvas = d.createElement('canvas')
    if (canvas.getContext) {
      var gl = canvas.getContext('webgl') || canvas.getContext('webgl-experimental')
      if (gl) {
        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
        if (debugInfo) {
          return {
            ven: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
            ren: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
          }
        }
      }
    }
  }

  function generateUid() {
    var uid = ''

    for (var i = 0; i < 8; i++) {
      uid =
        uid +
        Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1)
    }

    return uid
  }

  function getUid() {
    var gUid = 0
    var gCnt = 30
    var key = 'st_uid'
    if (!gUid) {
      gUid = (w.localStorage && w.localStorage.getItem(key)) || getCookie(key)
      if (!gUid) {
        gUid = generateUid()
        w.localStorage && w.localStorage.setItem(key, gUid)
        d.cookie = key + '=' + gUid + '; path=/; max-age=259200'
      }
    }
    try {
      if (cookieStore) {
        cookieStore.addEventListener('change', function(event) {
          if (
            ((event.changed &&
              event.changed.some(function(c) {
                return c.name === key
              })) ||
              (event.deleted &&
                event.deleted.some(function(c) {
                  return c.name === key
                }))) &&
            getCookie(key) !== gUid &&
            gCnt
          ) {
            w.localStorage && w.localStorage.setItem(key, gUid)
            d.cookie = key + '=' + gUid + '; path=/; max-age=259200'
            --gCnt
          }
        })
      }
    } catch (error) {}

    return gUid
  }

  function getInu() {
    var key = 'st_uid'

    if (!w.localStorage) {
      return 1
    }

    if (!w.localStorage.getItem(key)) {
      return 1
    } else {
      return 0
    }
  }

  function hit(referrer) {
    var s = w && w.sessionStorage ? w.sessionStorage : {}
    var query = {
      rnd: Math.random().toString(),
      u: encodeURIComponent(d.URL),
      r: encodeURIComponent(referrer || d.referrer),
      inu: getInu()
    }

    try {
      var e = d.documentElement
      query.v = 4
      query.uid = getUid()
      query.w = w.top === w ? 1 : 0
      query.h = d.hidden ? 1 : 0
      query.gW = Math.max(e.clientWidth, w.innerWidth || 0)
      query.gH = Math.max(e.clientHeight, w.innerHeight || 0)
      query.gDH = Math.max(
        d.body.scrollHeight,
        e.scrollHeight,
        d.body.offsetHeight,
        e.offsetHeight,
        d.body.clientHeight,
        e.clientHeight
      )
      query.gDW = Math.max(
        d.body.scrollWidth,
        e.scrollWidth,
        d.body.offsetWidth,
        e.offsetWidth,
        d.body.clientWidth,
        e.clientWidth
      )
      query.sW = sc.width || 0
      query.sH = sc.height || 0
      query.daw = sc.availWidth || 0
      query.dah = sc.availHeight || 0
      query.ga = getCookie('_ga')
      query.dpr = w.devicePixelRatio || ''
      query.c = (function() {
        var conn = ''
        if (nav && nav.connection) {
          if (nav.connection.type) conn = nav.connection.type
          else if (nav.connection.effectiveType) conn = 'eff:' + nav.connection.effectiveType
        }
        return conn
      })()
      query.t = s && s._tid ? s._tid : (s._tid = Date.now())

      if (w.performance) {
        if (w.performance.navigation) {
          query.rc = w.performance.navigation.redirectCount
          query.tn = w.performance.navigation.type
        }

        if (w.performance.timing)
          query.dc =
            (w.performance.timing.secureConnectionStart || w.performance.timing.fetchStart) -
            w.performance.timing.fetchStart
      }

      var wGL = getWGL()
      if (wGL) {
        query.wGLRen = wGL.ren
        query.wGLVen = wGL.ven
      }
    } catch (e) {}

    var path = '//statad.ru/pixel.gif'
    var qs = serialize(query)
    new Image().src = [path, '?', qs].join('')
  }

  hit()

  var url = w.location.href
  var count = 0
  var checkInterval = setInterval(function() {
    if (count >= 50) clearInterval(checkInterval)
    else if (url !== w.location.href) {
      hit(url)
      url = w.location.href
      count++
    }
  }, 1000)
})(document, window, navigator, screen)

/*
-----BEGIN PGP SIGNATURE-----
Version: OpenPGP.js v4.10.4
Comment: https://openpgpjs.org

wsDcBAEBCgAGBQJjDCrTAAoJEOOmc3IHnZzJHcQMAOpSncd8IiFbGXza/s1O
anI3S42smRAcm+CjvLMnJYToera4iHP6mjLooxPJRVwMKiGP30SSPUNQm2X0
cff1h8wos5Ffp+kUvGqNp7dk9fBLJyvpbtTRuIMXK1c2CkMO0sl6IvVdnplN
m939enWBaUm0h2fZ097Aj0bTnKf9DVr5dJMjLZzswE0Jcy8qQYRZM8OI8iBv
dd3T58AmiizvUiBZmJOnfOJ+PY9w7Y1VpT1BLiQ4w+ggKTJk04YSBslwtXx4
f6kkbjAOUaEKRnIyb3vI2w4rppQyx5oHBAitJVDE2nTxGZXWTrc9cpbCywDo
t3UtbZYX93OQ+fq0b1MQRT6p37Tg+beh1PXiQZEd23rURIhbKu+EGv3U1dDx
uQeLr95T0qkzcd3iM5EDZDtEvol5ktftMIZIhuhar3WVnZozBKdDpQ5n/vUC
oqSmRoVjtBAhd2hn/pES5eiskzjFCVmP9t8DggQCq4Kxg0W+Fqn0paoH58UX
S/sQI7uN9X1evw==
=Fj2q
-----END PGP SIGNATURE-----

*/