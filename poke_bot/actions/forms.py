from __future__ import annotations

from typing import Any

from rasa_sdk import FormValidationAction


class ValidatePokemonTypeForm(FormValidationAction):
    def name(self) -> str:
        return 'validate_pokemon_type_form'

    @staticmethod
    def cuisine_db() -> list[str]:
        """Database of supported cuisines"""

        return ["caribbean", "chinese", "french"]

    def validate_pokemon_name(self, slot_value: Any, *args, **kwargs) -> dict[str, Any]:
        if slot_value.lower() in self.cuisine_db():
            return {"pokemon_type": slot_value}
        return {'pokemon_type': None}
