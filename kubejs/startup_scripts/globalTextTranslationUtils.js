const $TranslationComponent = Java.loadClass("net.minecraft.network.chat.Component");

// 1.21.1: Text.of(NBT.stringTag(json)) no longer parses JSON, it renders the raw
// string. Build the translatable component directly; the explicit signature
// avoids Rhino's ambiguity with the (String,String,Object...) overload.
global.translatableWithFallback = (key, fallback) => {
    if (!fallback) return Text.translatable(key);
    return $TranslationComponent["translatableWithFallback(java.lang.String,java.lang.String)"](String(key), String(fallback));
}

global.getTranslatedEntityName = (entity_id, fallback) => {
    return global.translatableWithFallback(`entity.${entity_id.namespace}.${entity_id.path}`, fallback)
}

global.getTranslatedItemName = (item_id, fallback) => {
    const prefix = Item.of(item_id).block ? "block" : "item";
    return global.translatableWithFallback(`${prefix}.${item_id.namespace}.${item_id.path}`, fallback)
}

global.getTranslatedTextWithColorCode = (colorCode, key) => {
    switch(colorCode) {
        case "0":
            return Text.translatable(key).black();
        case "1":
            return Text.translatable(key).darkBlue();
        case "2":
            return Text.translatable(key).darkGreen();
        case "3":
            return Text.translatable(key).darkAqua();
        case "4":
            return Text.translatable(key).darkRed();
        case "5":
            return Text.translatable(key).darkPurple();
        case "6":
            return Text.translatable(key).gold();
        case "7":
            return Text.translatable(key).gray();
        case "8":
            return Text.translatable(key).darkGray();
        case "9":
            return Text.translatable(key).blue();
        case "a":
            return Text.translatable(key).green();
        case "b":
            return Text.translatable(key).aqua();
        case "c":
            return Text.translatable(key).red();
        case "d":
            return Text.translatable(key).lightPurple();
        case "e":
            return Text.translatable(key).yellow();
        case "f":
            return Text.translatable(key).white();
        default:
            return Text.translatable(key);
    }
}

global.getNotePaperItem = (author, text, title) => {
    // I want to check argument type and process it,
    // but I'm not sure how does instanceof work in runtime.
    // So, This method takes 3 strings.
    return Item.of(
            "candlelight:note_paper_written",
            `{author:"${author}",text:['${text}'],title:"${title}"}`
          )
}

global.getEmbersTextAPICommand = (target, design, duration, text) => {
    return `emberstextapi sendcustom ${target} ${design} ${duration} ${text}`
}
