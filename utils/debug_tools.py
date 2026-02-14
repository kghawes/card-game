"""
This module contains tools for in-game debugging.
"""
import utils.constants as c

class DebugTools:
    """
    Class for in-game debugging tools.
    """
    def __init__(self, event_manager, registries):
        self.event_manager = event_manager
        self.registries = registries
        self.commands = {
            "HELP": DebugCommand(
                "/h[elp] [<command>]",
                "Show this help message or usage for a given command. Hit ` to close the console.",
                "Yes, exactly like that.",
                self.help_cmd
            ),
            "RESOLVE": DebugCommand(
                "/r[esolve] <effect> <target> <level>",
                "Resolves an effect by name, target, and level.",
                "Usage: <effect> must be a valid effect name (use either spaces or underscores). <target> must be self or enemy. <level> must be a positive integer.\\nUse /r apply [status] [target] [level] to apply a status.",
                self.resolve_effect_cmd
            ),
            "ADD": DebugCommand(
                "/a[dd] <card> [<quantity>]",
                "Adds a card to the player's hand.",
                "Usage: <card> must be a valid card ID. <quantity> is optional.",
                self.add_card_cmd
            ),
            "SET": DebugCommand(
                "/s[et] <target> [max] <stat> <value>",
                "Sets a player's resource or attribute to a given value.",
                "Usage: <target> must be self or enemy. <stat> must be the name of a resource or character attribute. <value> must be an integer.\\nUse /s <target> max <resource> <value> to set a resource's maximum value.",
                self.set_stat_cmd
            )
        }
    
    def parse_command(self, input_str, player, enemy):
        """
        Parses a debug command and executes the corresponding action.
        """
        if not input_str.strip():
            raise ValueError("Debug command cannot be empty.")
        
        parts = input_str.strip().upper().split()
        cmd = parts[0]
        args = parts[1:]
        if cmd.startswith("/"):
            cmd = cmd[1:]

        success, message = False, "Unknown command."
        for command_name, command in self.commands.items():
            if command_name.startswith(cmd):
                try:
                    success, message = command.execute(*args)
                except Exception as e:
                    message = str(e)
                break
        self.event_manager.dispatch("debug_command_executed", input_str, success, message)
    
    def help_cmd(self, player, enemy, *args) -> tuple:
        """
        Shows a help message with available debug commands.
        """
        if args.count == 0:
            message = "Available commands:\\n"
            for command in self.commands.values():
                message += f"{command.name}\\n{command.description}\\n"
            return True, message
        else:
            for cmd in args:
                for command_name, command in self.commands.items():
                    if command_name.startswith(cmd):
                        message += f"{command.name}\\n{command.description}\\n{command.help_text}\\n"
            return True, message

    def resolve_effect_cmd(self, player, enemy, *args) -> tuple:
        """
        Resolves an effect given its ID and level.
        """
        level = args.pop()
        effect_id = "_".join(args)
        if level.isdigit():
            level = int(level)
            if level <= 0:
                return False, "Level must be a positive integer."
        else:
            return False, "Level must be a positive integer."
        effect = self.registries.effects.get_effect(effect_id)
        if effect:
            effect.resolve(player, enemy, level, self.registries.statuses)

    def add_card_cmd(self, player, enemy, *args) -> tuple:
        """
        Adds a card to the player's hand given its ID.
        """
        pass

    def set_stat_cmd(self, player, enemy, *args) -> tuple:
        """
        Sets a combatant's stat to a given value.
        """
        pass


class DebugCommand():
    """
    Represents a debug command with its execution logic.
    """
    def __init__(self, name: str, description: str, help_text: str, fun: callable):
        """
        Initialize a new DebugCommand.
        """
        self.name = name
        self.description = description
        self.help_text = help_text
        self.fun = fun
    
    def execute(self, *args, **kwargs):
        """
        Executes the debug command with the provided arguments.
        """
        return self.fun(*args, **kwargs)
