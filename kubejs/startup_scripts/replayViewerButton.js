// Mantem o botao do Replay Viewer (ReplayMod / ReForged Play Mod) alinhado ao menu
// inicial do FancyMenu.
//
// O FancyMenu reposiciona os botoes vanilla pelo layout, mas nao consegue identificar
// o botao do ReplayMod (ele nao tem identificador universal), entao o mod calcula a
// posicao dele sozinho, na inicializacao da tela, e o botao acaba sobrepondo o menu.
//
// Este script coloca o botao do Replay Viewer na mesma coluna dos icones de
// acessibilidade e idioma (a direita dos botoes do menu), na linha do botao
// "Multiplayer", antes de cada frame da tela ser desenhado.
//
// Por que aqui em `startup_scripts` e nao em `client_scripts`:
// - `ClientEvents.tick` nao roda na tela inicial: o KubeJS sai do handler quando nao
//   existe mundo/jogador carregado (MinecraftClientMixin.kjs$postTickClient).
// - `ClientEvents.paintScreen` tem a mesma trava (Painter.guiScreenDraw).
// - `ForgeEvents` so e registrado nos scripts de startup (BuiltinKubeJSForgePlugin).
//
// ATENCAO: dentro de funcao, e principalmente dentro de `try`, usar `var` e nunca
// `const`/`let`. O Rhino do KubeJS estoura "redeclaration of var <nome>" quando o
// bloco declara const/let (ver decisions.md de 2026-10-29, entrada do Replay Viewer).

var REPLAY_BUTTON_CLASS_PREFIX = "com.replaymod.replay.handler.GuiHandler$";
var RENDER_EVENT = Java.loadClass("net.neoforged.neoforge.client.event.ScreenEvent$Render$Pre");
var REPLAY_VIEWER_KEY = "replaymod.gui.replayviewer";
var MULTIPLAYER_BUTTON_KEY = "menu.multiplayer";
var MODS_BUTTON_KEY = "fml.menu.mods";
var ACCESSIBILITY_BUTTON_KEY = "options.accessibility";

// Os botoes do menu tem 200 de largura no layout + 2 de respiro, entao a coluna dos
// icones fica 202 a direita do botao. So serve de reserva, o normal e pegar a coluna
// do proprio icone de acessibilidade.
var ICON_COLUMN_OFFSET = 202;

var labels = null;
var loggedError = false;
var loggedPlacement = false;

function widgetLabel(widget) {
  try {
    var message = widget.getMessage();
    return message == null ? null : message.getString();
  } catch (error) {
    return null;
  }
}

function loadLabels() {
  return {
    replayViewer: Component.translatable(REPLAY_VIEWER_KEY).getString(),
    multiplayer: Component.translatable(MULTIPLAYER_BUTTON_KEY).getString(),
    mods: Component.translatable(MODS_BUTTON_KEY).getString(),
    accessibility: Component.translatable(ACCESSIBILITY_BUTTON_KEY).getString(),
  };
}

// O FancyMenu guarda a posicao dos widgets que ele controla em customX/customY e o
// getX()/getY() do mixin passa a devolver esses campos. setPosition so mexe no campo
// vanilla, entao quando o FancyMenu ja marcou o widget e preciso gravar nos dois
// lugares (widget sem esses metodos apenas ignora).
function applyPosition(widget, x, y) {
  widget.setPosition(x, y);

  try {
    if (widget.getX() != x) {
      widget.setCustomXFancyMenu(x);
    }
    if (widget.getY() != y) {
      widget.setCustomYFancyMenu(y);
    }
  } catch (error) {
    // widget que nao e do FancyMenu
  }
}

function placeReplayButton(screen) {
  if (screen == null) {
    return;
  }

  if (labels == null) {
    labels = loadLabels();
  }

  var replayButton = null;
  var multiplayerButton = null;
  var modsButton = null;
  var accessibilityButton = null;

  var children = screen.children();
  for (var i = 0; i < children.size(); i++) {
    var widget = children.get(i);
    var className = null;
    try {
      className = "" + widget.getClass().getName();
    } catch (error) {
      continue;
    }
    var label = widgetLabel(widget);

    if (className.indexOf(REPLAY_BUTTON_CLASS_PREFIX) == 0) {
      // Na tela inicial o botao do Replay Viewer nao tem texto (so tooltip). O botao
      // "Sair do replay" da tela de pausa tem texto e nao deve ser movido.
      // `label == ""` (e nao `label.length`) porque o texto pode chegar como texto do
      // Java ou como texto do proprio Rhino, e a comparacao por conteudo funciona nos dois.
      if (label == null || label == "" || label == labels.replayViewer) {
        replayButton = widget;
      }
      continue;
    }

    if (label == null) {
      continue;
    }
    if (label == labels.replayViewer) {
      // Reserva para outra versao do mod, que desenha o botao com texto.
      replayButton = widget;
    } else if (label == labels.multiplayer) {
      multiplayerButton = widget;
    } else if (label == labels.mods) {
      modsButton = widget;
    } else if (label == labels.accessibility) {
      accessibilityButton = widget;
    }
  }

  var anchor = multiplayerButton != null ? multiplayerButton : modsButton;
  if (replayButton == null || anchor == null) {
    return;
  }

  var x =
    accessibilityButton != null
      ? accessibilityButton.getX()
      : anchor.getX() + ICON_COLUMN_OFFSET;
  var y = anchor.getY() + Math.round((anchor.getHeight() - replayButton.getHeight()) / 2);

  if (replayButton.getX() == x && replayButton.getY() == y) {
    return;
  }

  var before = replayButton.getX() + "," + replayButton.getY();
  applyPosition(replayButton, x, y);

  if (!loggedPlacement) {
    loggedPlacement = true;
    console.info(
      "[Sunlit] Botao do Replay Viewer: " +
        before +
        " -> " +
        replayButton.getX() +
        "," +
        replayButton.getY() +
        " (tela " +
        screen.getClass().getName() +
        ", ancora " +
        anchor.getX() +
        "," +
        anchor.getY() +
        ")"
    );
  }
}

function onScreenRender(event) {
  try {
    placeReplayButton(event.getScreen());
  } catch (error) {
    if (!loggedError) {
      loggedError = true;
      console.error("[Sunlit] Falha ao reposicionar o botao do Replay Viewer: " + error);
    }
  }
}

try {
  NativeEvents.onEvent(RENDER_EVENT, onScreenRender);
} catch (error) {
  // Servidor dedicado nao tem tela de cliente; no cliente isso nao deve acontecer.
  console.warn("[Sunlit] Botao do Replay Viewer nao registrado: " + error);
}
