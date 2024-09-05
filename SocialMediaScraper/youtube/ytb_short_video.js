// Generates the APISIDDHASH / SAPISIDHASH token Google uses in the Authorization header of some API requests
// Usage: node google_token_hash_generator.js <TOKEN> <DOMAIN>

var TOKEN = "__fw"; // APISID / SAPISID token (base64)
var DOMAIN = "https://www.youtube.com"; // Domain name, including https://, without trailing slash

var $gb = function () {
  function a() {
    e[0] = 1732584193;
    e[1] = 4023233417;
    e[2] = 2562383102;
    e[3] = 271733878;
    e[4] = 3285377520;
    n = m = 0
  }
  function b(p) {
    for (var r = g, t = 0; 64 > t; t += 4) r[t / 4] = p[t] << 24 | p[t + 1] << 16 | p[t + 2] << 8 | p[t + 3];
    for (t = 16; 80 > t; t++) p = r[t - 3] ^ r[t - 8] ^ r[t - 14] ^ r[t - 16],
    r[t] = (p << 1 | p >>> 31) & 4294967295;
    p = e[0];
    var x = e[1],
    y = e[2],
    A = e[3],
    K = e[4];
    for (t = 0; 80 > t; t++) {
      if (40 > t) if (20 > t) {
        var L = A ^ x & (y ^ A);
        var U = 1518500249
      } else L = x ^ y ^ A,
      U = 1859775393;
       else 60 > t ? (L = x & y | A & (x | y), U = 2400959708) : (L = x ^ y ^ A, U = 3395469782);
      L = ((p << 5 | p >>> 27) & 4294967295) +
      L + K + U + r[t] & 4294967295;
      K = A;
      A = y;
      y = (x << 30 | x >>> 2) & 4294967295;
      x = p;
      p = L
    }
    e[0] = e[0] + p & 4294967295;
    e[1] = e[1] + x & 4294967295;
    e[2] = e[2] + y & 4294967295;
    e[3] = e[3] + A & 4294967295;
    e[4] = e[4] + K & 4294967295
  }
  function c(p, r) {
    if ('string' === typeof p) {
      p = unescape(encodeURIComponent(p));
      for (var t = [
      ], x = 0, y = p.length; x < y; ++x) t.push(p.charCodeAt(x));
      p = t
    }
    r || (r = p.length);
    t = 0;
    if (0 == m) for (; t + 64 < r; ) b(p.slice(t, t + 64)),
    t += 64,
    n += 64;
    for (; t < r; ) if (f[m++] = p[t++], n++, 64 == m) for (m = 0, b(f); t + 64 < r; ) b(p.slice(t, t + 64)),
    t += 64,
    n += 64
  }
  function d() {
    var p = [
    ],
    r = 8 * n;
    56 > m ? c(h, 56 - m) : c(h, 64 - (m - 56));
    for (var t = 63; 56 <= t; t--) f[t] = r & 255,
    r >>>= 8;
    b(f);
    for (t = r = 0; 5 > t; t++) for (var x = 24; 0 <= x; x -= 8) p[r++] = e[t] >> x & 255;
    return p
  }
  for (var e = [
  ], f = [
  ], g = [
  ], h = [
    128
  ], k = 1; 64 > k; ++k) h[k] = 0;
  var m,
  n;
  a();
  return {
    reset: a,
    update: c,
    digest: d,
    digestString: function () {
      for (var p = d(), r = '', t = 0; t < p.length; t++) r += '0123456789ABCDEF'.charAt(Math.floor(p[t] / 16)) + '0123456789ABCDEF'.charAt(p[t] % 16);
      return r
    }
  }
}

var hash = $gb();
var date = Math.floor(new Date() / 1000);
hash.update(date + " " + TOKEN + " " + DOMAIN);
var result = date + "_" + hash.digestString().toLowerCase();
process.stdout.write(result);