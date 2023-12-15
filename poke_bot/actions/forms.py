from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rasa_sdk import FormValidationAction, Tracker
from rasa_sdk.types import DomainDict

if TYPE_CHECKING:
    from rasa_sdk.executor import CollectingDispatcher


class ValidatePokemonTypeForm(FormValidationAction):
    def name(self) -> str:
        return 'validate_pokemon_type_form'

    @staticmethod
    def cuisine_db() -> list[str]:
        """Database of supported cuisines"""

        return ["caribbean", "chinese", "french"]

    def validate_pokemon_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> dict[str, Any]:
        if slot_value.lower() in self.cuisine_db():
            return {"pokemon_type": slot_value}
        return {'pokemon_type': None}
