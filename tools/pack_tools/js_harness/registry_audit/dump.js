(function () {
  var out = { trades: {}, lists: {}, machines: {}, canonical: global.canonicalItems || {}, processValue: global.processValue || {}, logs: __logs, globals: Object.keys(global) };
  global.trades.forEach(function (v, k) { out.trades[String(k)] = { v: v.value, m: String(v.multiplier).replace('shippingbin:', '').replace('_sell_multiplier', '') }; });
  Object.keys(global).forEach(function (n) {
    var g = global[n];
    if (Array.isArray(g) && g.length && g[0] && g[0].item) out.lists[n] = g.map(function (e) { return { item: String(e.item), value: e.value }; });
    if (/Recipes$/.test(n) && g && g.forEach && !Array.isArray(g)) {
      var m = {}; g.forEach(function (v, k) { m[String(k)] = v && v.output ? v.output.map(String) : null; });
      out.machines[n] = m;
    }
  });
  return JSON.stringify(out);
})();
