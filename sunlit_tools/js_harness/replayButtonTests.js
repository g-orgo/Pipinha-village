// Testes do kubejs/startup_scripts/replayViewerButton.js (roda com o Rhino do KubeJS).
// Cada cenario monta uma tela inicial falsa, dispara um frame (ScreenEvent$Render$Pre)
// e confere a posicao final do botao do Replay Viewer.

var failures = 0;

function check(name, cond, detail) {
  if (cond) {
    print('PASS ' + name);
  } else {
    failures++;
    print('FAIL ' + name + (detail === undefined ? '' : ' -> ' + detail));
  }
}

function errosOuAvisos() {
  return LOG.filter(function (m) {
    return m.indexOf('ERROR') === 0 || m.indexOf('WARN') === 0;
  });
}

var REPLAY_CLASS = 'com.replaymod.replay.handler.GuiHandler$1';
var BTN = 'net.minecraft.client.gui.components.Button';
var IMG = 'net.minecraft.client.gui.components.ImageButton';

function layout(replayX, replayY) {
  return {
    singleplayer: widget(BTN, 'Singleplayer', 16, -43, 200, 32),
    multiplayer: widget(BTN, 'Multiplayer', 16, -9, 200, 32),
    options: widget(BTN, 'Options', 16, 25, 200, 32),
    mods: widget(BTN, 'Mods', 16, 59, 200, 32),
    accessibility: widget(IMG, 'Accessibility Options', 218, 59, 32, 32),
    quit: widget(BTN, 'Quit', 16, 93, 200, 32),
    language: widget(IMG, 'Language', 218, 93, 20, 20),
    replay: widget(REPLAY_CLASS, '', replayX, replayY, 20, 20),
  };
}

function listOf(l) {
  return [l.singleplayer, l.multiplayer, l.options, l.mods, l.accessibility, l.quit, l.language, l.replay];
}

// 0) registrou o evento de render (ForgeEvents so existe em startup_scripts)
check(
  'registra ScreenEvent$Render$Pre',
  RENDER_EVENT_NAME === 'net.minecraftforge.client.event.ScreenEvent$Render$Pre',
  RENDER_EVENT_NAME
);

// 1) layout completo: coluna dos icones (218) na linha do Multiplayer (-9 + 6)
var l = layout(100, 100);
MC.screen = screenOf(TITLE, listOf(l));
RENDER_FRAME();
check(
  'cola na coluna dos icones, na linha do Multiplayer',
  l.replay.pos.x === 218 && l.replay.pos.y === -3,
  l.replay.pos.x + ',' + l.replay.pos.y
);
check('nao sobrepoe o botao Multiplayer', l.replay.pos.x >= l.multiplayer.pos.x + l.multiplayer.getWidth());

// 2) idempotente: segundo frame nao mexe de novo
var movesAntes = l.replay.moves.length;
RENDER_FRAME();
check('segundo frame nao reposiciona', l.replay.moves.length === movesAntes, l.replay.moves.join(' | '));

// 3) sem o icone de acessibilidade: usa o offset 202 do proprio botao do menu
var l3 = layout(100, 100);
l3.multiplayer.pos.x = 20;
MC.screen = screenOf(TITLE, [l3.singleplayer, l3.multiplayer, l3.mods, l3.replay]);
RENDER_FRAME();
check(
  'sem icone de acessibilidade usa 202 de offset',
  l3.replay.pos.x === 222 && l3.replay.pos.y === -3,
  l3.replay.pos.x + ',' + l3.replay.pos.y
);

// 4) sem Multiplayer (menu modificado): cai para o botao Mods
var l4 = layout(100, 100);
MC.screen = screenOf(TITLE, [l4.singleplayer, l4.mods, l4.accessibility, l4.replay]);
RENDER_FRAME();
check(
  'sem Multiplayer ancora no Mods',
  l4.replay.pos.x === 218 && l4.replay.pos.y === 65,
  l4.replay.pos.x + ',' + l4.replay.pos.y
);

// 5) tela sem o botao do ReplayMod: nao mexe em nada nem loga erro
var l5 = layout(100, 100);
MC.screen = screenOf(TITLE, [l5.singleplayer, l5.multiplayer, l5.accessibility]);
RENDER_FRAME();
check('tela sem botao do Replay Viewer nao quebra', errosOuAvisos().length === 0, LOG.join(' | '));

// 6) fora da tela inicial (pausa): nao mexe, nem no botao "Sair do replay"
var l6 = layout(100, 100);
l6.replay = widget(REPLAY_CLASS, 'Exit Replay', 100, 100, 20, 20);
MC.screen = screenOf('net.minecraft.client.gui.screens.PauseScreen', listOf(l6));
RENDER_FRAME();
check('outras telas sao ignoradas', l6.replay.pos.x === 100 && l6.replay.pos.y === 100, l6.replay.pos.x + ',' + l6.replay.pos.y);

// 7) tela nula (carregando): nao quebra
MC.screen = null;
RENDER_FRAME();
check('tela nula nao quebra', errosOuAvisos().length === 0, LOG.join(' | '));

// 8) resize do FancyMenu: ancora mudou, o botao acompanha
var l8 = layout(218, -3);
l8.multiplayer.pos.x = 40;
l8.multiplayer.pos.y = 10;
MC.screen = screenOf(TITLE, listOf(l8));
RENDER_FRAME();
check('acompanha o menu depois de um resize', l8.replay.pos.x === 218 && l8.replay.pos.y === 16, l8.replay.pos.x + ',' + l8.replay.pos.y);

// 9) botao do ReplayMod com outra classe (outra versao do mod): acha pelo texto
var l9 = layout(100, 100);
l9.replay = widget('com.example.WrappedButton', 'Replay Viewer', 100, 100, 20, 20);
MC.screen = screenOf(TITLE, listOf(l9));
RENDER_FRAME();
check('acha o botao pelo texto quando a classe muda', l9.replay.pos.x === 218 && l9.replay.pos.y === -3, l9.replay.pos.x + ',' + l9.replay.pos.y);

// 10) widget que estoura no getMessage e ignorado
var quebrado = widget('com.example.Quebrado', 'x', 0, 0, 10, 10);
quebrado.getMessage = function () { throw new Error('boom'); };
var l10 = layout(100, 100);
MC.screen = screenOf(TITLE, [quebrado].concat(listOf(l10)));
RENDER_FRAME();
check('widget problemático nao impede o reposicionamento', l10.replay.pos.x === 218 && l10.replay.pos.y === -3, l10.replay.pos.x + ',' + l10.replay.pos.y);

// 11) erro real: loga uma vez so, sem repetir a cada frame
var l11 = layout(100, 100);
var telaQuebrada = screenOf(TITLE, listOf(l11));
telaQuebrada.children = function () { throw new Error('falha simulada'); };
MC.screen = telaQuebrada;
RENDER_FRAME();
RENDER_FRAME();
var erros = LOG.filter(function (m) { return m.indexOf('ERROR') === 0; });
check('erro e logado uma unica vez', erros.length === 1, LOG.join(' | '));

// 12) FancyMenu marcou o widget: getX()/getY() devolvem customX/customY
var l12 = layout(100, 100);
l12.replay.custom.x = 900;
l12.replay.custom.y = 900;
MC.screen = screenOf(TITLE, listOf(l12));
RENDER_FRAME();
check(
  'posicao customizada do FancyMenu tambem e atualizada',
  l12.replay.getX() === 218 && l12.replay.getY() === -3 && l12.replay.custom.x === 218 && l12.replay.custom.y === -3,
  l12.replay.getX() + ',' + l12.replay.getY() + ' custom ' + l12.replay.custom.x + ',' + l12.replay.custom.y
);

// 13) o log de confirmacao aparece uma vez so
var logsPosicao = LOG.filter(function (m) { return m.indexOf('INFO [Sunlit] Botao do Replay Viewer:') === 0; });
check('loga o posicionamento uma unica vez', logsPosicao.length === 1, LOG.join(' | '));
check(
  'log mostra a posicao antiga e a nova',
  logsPosicao.length === 1 && logsPosicao[0].indexOf('100,100 -> 218,-3') > 0,
  logsPosicao.join(' | ')
);

print(failures === 0 ? 'TODOS OS TESTES PASSARAM' : failures + ' TESTE(S) FALHARAM');
var RESULT = failures;
