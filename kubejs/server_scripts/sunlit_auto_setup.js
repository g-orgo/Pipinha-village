// Sunlit piloto automatico: garante o scoreboard usado pelo datapack (idempotente).
ServerEvents.loaded(event => {
  event.server.runCommandSilent('scoreboard objectives add sunlit_t dummy')
})
