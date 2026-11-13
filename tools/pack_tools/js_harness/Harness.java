import dev.latvian.mods.rhino.Context;
import dev.latvian.mods.rhino.Scriptable;
import java.io.FileReader;
import java.io.Reader;

/**
 * Roda os scripts de startup do KubeJS fora do jogo, no Rhino do próprio mod.
 * Cada script ganha um escopo próprio com o escopo compartilhado como protótipo
 * (como o KubeJS faz) e é avaliado duas vezes, simulando cliente + servidor.
 */
public class Harness {
    static Context cx;
    static Scriptable shared;

    static void evalFile(String path) throws Exception {
        Scriptable local = cx.newObject(shared);
        local.setPrototype(shared);
        try (Reader r = new FileReader(path)) {
            cx.evaluateReader(local, r, path, 1, null);
            System.out.println("OK   " + path);
        }
    }

    static void evalShared(String src) {
        cx.evaluateString(shared, src, "<stub>", 1, null);
    }

    public static void main(String[] args) throws Exception {
        cx = Context.enter();
        shared = cx.initStandardObjects();

        // stubs mínimos do KubeJS
        evalShared("var __log = []; var print = function (m) { __log.push(String(m)); };");
        evalShared("var console = { info: function (m) { print(m); }, warn: function (m) { print('WARN ' + m); } };");
        evalShared("var global = {};");
        evalShared("global.getConfiguredValue = function (v, m) { return Math.round(v); };");
        evalShared("global.formatPrice = function (v) { return String(v); };");

        evalFile("/w/data.js");
        evalShared("global.trades = new Map();");
        evalShared("[global.crops, global.cocktails].forEach(function (list) { list.forEach(function (e) { global.trades.set(e.item, { value: e.value, multiplier: 'shippingbin:crop_sell_multiplier' }); }); });");
        evalShared("['society:milk','meadow:piece_of_cheese','minecraft:egg','society:mayonnaise','society:oil','minecraft:torchflower','vinery:red_wine','hearthandharvest:blueberries'].forEach(function (id, i) { global.trades.set(id, { value: [16,24,4,16,70,128,336,24][i], multiplier: 'shippingbin:crop_sell_multiplier' }); });");

        System.out.println("-- 1a avaliacao --");
        evalFile("/w/globalPriceBalance.js");
        evalFile("/w/globalProcessValue.js");
        System.out.println("-- 2a avaliacao (cliente + servidor) --");
        evalFile("/w/globalPriceBalance.js");
        evalFile("/w/globalProcessValue.js");

        evalShared("print('blueberry=' + global.trades.get('society:blueberry').value + ' wheat=' + global.trades.get('minecraft:wheat').value + ' crate=' + global.trades.get('society:blueberry_crate').value + ' hay=' + global.trades.get('minecraft:hay_block').value + ' mana=' + global.trades.get('society:mana_fruit').value);");
        evalShared("print('itens com bonus: ' + Object.keys(global.processValue).length);");
        evalShared("['society:mayonnaise','meadow:piece_of_cheese','vinery:red_wine','vintagedelight:pickle'].forEach(function (id) { var i = global.processValue[id]; print(id + ' -> ' + (i ? ('+' + i + ' (moedas|%)') : 'sem bonus')); });");

        try (Reader r = new FileReader("/w/addPriceTooltips.js")) {
            cx.compileReader(r, "/w/addPriceTooltips.js", 1, null);
            System.out.println("OK   addPriceTooltips.js (sintaxe)");
        }

        System.out.println("---- log ----");
        System.out.println(cx.toString(cx.evaluateString(shared, "__log.join('\\n')", "<log>", 1, null)));
    }
}
