// Opens a shop or selector chosen in a dialog option.
// SVDialog 1.6 sends an option's command to the server and then jumps to the option's target.
// The "end" target closes the dialog screen 500 ms later with Screen.onClose(), which also closes
// any shop that opened in the meantime, so the player only saw the dialog close.
// Dialog options call "dialogshop shop <id>" or "dialogshop selector <id>" instead, and the
// shop opens after that fade-out. Entry-level commands (chatter) do not fade and keep openshop.
ServerEvents.commandRegistry((event) => {
  const { commands: Commands, arguments: Arguments } = event;
  const delayTicks = 20;

  let openAfterDialog = (source, kind, id) => {
    let player = source.player;
    let command = String(kind) == "selector" ? "openselector" : "openshop";
    let shopId = String(id);
    let name;
    let server;
    if (!player) return 0;
    name = String(player.username);
    server = player.server;
    server.scheduleInTicks(delayTicks, () => {
      server.runCommandSilent(`${command} ${name} ${shopId}`);
    });
    return 1;
  };

  event.register(
    Commands.literal("dialogshop")
      .requires((source) => source.hasPermission(2))
      .then(
        Commands.argument("kind", Arguments.STRING.create(event)).then(
          Commands.argument("id", Arguments.STRING.create(event)).executes((c) =>
            openAfterDialog(c.source, Arguments.STRING.getResult(c, "kind"), Arguments.STRING.getResult(c, "id"))
          )
        )
      )
  );
});
