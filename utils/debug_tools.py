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
                "/r[esolve] <effect> <combatant> <level>",
                "Resolves an effect by name, target, and level.",
                "Usage: <effect> must be a valid effect name (use either spaces or underscores). <combatant> must be self or target. <level> must be a positive integer.\nUse /r apply [status] [combatant] [level] to apply a status.",
                self.resolve_effect_cmd
            ),
            "ADD": DebugCommand(
                "/a[dd] <card> [<quantity>]",
                "Adds a card to the player's hand.",
                "Usage: <card> must be a valid card ID. <quantity> is optional.",
                self.add_card_cmd
            ),
            "SET": DebugCommand(
                "/s[et] <combatant> [max] <stat> <value>",
                "Sets a player's resource or attribute to a given value.",
                "Usage: <combatant> must be self or target. <stat> must be the name of a resource or character attribute. <value> must be an integer.\nUse /s <combatant> max <resource> <value> to set a resource's maximum value.",
                self.set_stat_cmd
            )
        }
    
    def execute_command(self, input_str, player, enemy):
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
                success, message = command.execute(player, enemy, args)
                break
        self.event_manager.dispatch("debug_command_executed", input_str, success, message)
    
    def help_cmd(self, player, enemy, args) -> tuple:
        """
        Shows a help message with available debug commands.
        """
        message = ""
        if len(args) > 0:
            found_command = False
            for cmd in args:
                if cmd.startswith("/"):
                    cmd = cmd[1:]
                for command_name, command in self.commands.items():
                    if command_name.startswith(cmd):
                        message += f"{command.name}\n{command.description}\n{command.help_text}\n"
                        found_command = True
                        break
            if found_command:
                return True, message
            else:
                message = "Command not found.\n"
        message += "Available commands:\n"
        for command in self.commands.values():
            message += f"{command.name}\n{command.description}\n"
        return True, message

    def resolve_effect_cmd(self, player, enemy, args) -> tuple:
        """
        Resolves an effect given its ID and level.
        """
        if len(args) < 3:
            return False, "Not enough arguments."
        level = args.pop()
        effect_id = "_".join(args)
        try:
            level = int(level)
            if level <= 0:
                return False, "Level must be a positive integer."
        except ValueError:
            return False, "Level must be a positive integer."
        effect = self.registries.effects.get_effect(effect_id)
        if effect:
            effect.resolve(player, enemy, level, self.registries)
            return True, f"Resolved {effect_id} {level}."
        else:
            return False, "Effect not found."

    def add_card_cmd(self, player, enemy, args) -> tuple:
        """
        Adds a card to the player's hand given its ID.
        """
        if len(args) < 1:
            return False, "Not enough arguments."
        quantity = 1
        try:
            quantity = int(args[-1])
            if quantity <= 0:
                return False, "Quantity must be a positive integer."
            args = args[:-1]
        except (ValueError, IndexError):
            # No quantity provided, default to 1
            pass
        card_id = "_".join(args)
        for _ in range(quantity):
            try:
                card = self.registries.cards.create_card(card_id, self.registries.effects)
                # TODO: roll card cache into registries
                if card:
                    result = player.card_manager.try_add_to_deck(card)
                    if not result[0]:
                        return False, "Card won't fit in deck."
                    player.card_manager.draw(player, self.registries)
                else:
                    return False, "Card not found."
            except Exception as e:
                return False, str(e)
        return True, f"Added {quantity} {card_id}(s)."

    def set_stat_cmd(self, player, enemy, args) -> tuple:
        """
        Sets a combatant's stat to a given value.
        """
        if len(args) < 3:
            return False, "Not enough arguments."
        
        target_str = args.pop(0)
        if target_str == "SELF":
            target = player
        elif target_str == "TARGET":
            target = enemy
        else:
            return False, "Combatant must be self or target."
        
        if args[0] == "MAX":
            args.pop(0)
            is_max = True
        else:
            is_max = False

        stat_id = args.pop(0)

        value_str = args.pop(0)
        try:
            value = int(value_str)
        except ValueError:
            return False, "Value must be an integer."

        if stat_id in list(c.Resources.__members__):
            if value < 0:
                return False, "Resources must be non-negative."
            mm = target.modifier_manager
            resource = target.resources[stat_id]
            if is_max:
                resource.max_value = value
                resource.current = resource.clamp_value(resource.current, mm)
                return True, f"Set {target_str.lower()} max {stat_id.lower()} = {value}."
            else:
                value = resource.clamp_value(value, mm)
                resource.current = value
                return True, f"Set {target_str.lower()} {stat_id.lower()} = {value}."
        elif stat_id in list(c.Attributes.__members__):
            target.attributes[stat_id] = value
            return True, f"Set {target_str.lower()} {stat_id.lower()} = {value}."
        return False, "Stat must be a valid resource or attribute."

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
