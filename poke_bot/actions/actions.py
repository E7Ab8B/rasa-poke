from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from aiohttp.client_exceptions import ClientError

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet

from .utils.requests import (
    check_pokemon_existence,
    pokemon_count,
    retrieve_all_pokemon_types,
    retrieve_pokemon_types,
    verify_pokemon_type,
)

if TYPE_CHECKING:
    from rasa_sdk.executor import CollectingDispatcher

logger = logging.getLogger(__name__)


class ActionCheckPokemonExistence(Action):
    """Action class to check the existence of a Pokémon and provide a response.

    Checks if a Pokemon provided in the 'pokemon_name' slot exists in the
    Poke API.
    If there is an error during the API request, it sends an error message.
    Otherwise, it responds with a template message indicating whether the
    Pokémon exists or not.
    """

    def name(self) -> str:
        return 'action_pokemon_existence'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, *args, **kwargs) -> list[dict[str, Any]]:
        pokemon_name = tracker.get_slot('pokemon_name')

        if not pokemon_name:
            dispatcher.utter_message(response='utter_pokemon_name_not_found')
            return []

        try:
            exists = await check_pokemon_existence(pokemon_name)
        except ClientError:
            logger.exception('Failed to check pokemon existence.')
            dispatcher.utter_message(response='utter_pokeapi_error')
            self.clear_pokemon_name()
            return []

        if exists:
            dispatcher.utter_message(
                response='utter_pokemon_exists',
                pokemon_name=pokemon_name,
            )
        else:
            dispatcher.utter_message(
                response='utter_pokemon_no_exist',
                pokemon_name=pokemon_name,
            )
            self.clear_pokemon_name()

        return []

    @staticmethod
    def clear_pokemon_name() -> None:
        SlotSet('pokemon_name', None)


class ActionVerifyPokemonType(Action):
    """Action class to verify the type of a Pokémon and provide a response.

    This action should be run when the form is completed and all required
    slots are filled.
    It retrieves information from the Poke API to verify the Pokémon's type
    and generates a response based on whether the Pokémon's type matches
    the expected type.
    """

    def name(self) -> str:
        return 'action_verify_pokemon_type'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, *args, **kwargs) -> list[dict[str, Any]]:
        pokemon_name = tracker.get_slot('pokemon_name')
        pokemon_type = tracker.get_slot('pokemon_type')

        assert pokemon_name and pokemon_type, 'Required slots must be set'

        try:
            verified = await verify_pokemon_type(pokemon_name, pokemon_type)
        except (ClientError, KeyError):
            logger.exception('Failed to verify pokemon type.')
            dispatcher.utter_message(response='utter_pokeapi_error')
            return []

        response = 'utter_confirm_pokemon_type' if verified else 'utter_pokemon_type_deny'
        dispatcher.utter_message(
            response=response,
            pokemon_name=pokemon_name,
            pokemon_type=pokemon_type,
        )

        return []


class ActionGetPokemonTypes(Action):
    """Action class for retrieving the types of a Pokémon.

    This action queries an external API to retrieve the types of a given Pokémon
    based on the provided `pokemon_name` slot. It then sends a message to the user
    with the Pokémon name and its associated types.

    It retrieves information from the Poke API to get all the Pokémon's types
    and generates a response.

    If the `pokemon_name` slot is not found, an error message is sent instead.
    """

    def name(self) -> str:
        return 'action_get_pokemon_types'

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, *args, **kwargs) -> list[dict[str, Any]]:
        pokemon_name = tracker.get_slot('pokemon_name')

        if not pokemon_name:
            dispatcher.utter_message(response='utter_pokemon_name_not_found')
            return []

        try:
            pokemon_types = await retrieve_pokemon_types(pokemon_name)
        except (ClientError, KeyError):
            logger.exception('Failed to get pokemon types.')
            dispatcher.utter_message(response='utter_pokeapi_error')
            return []

        if len(pokemon_types) == 1:
            dispatcher.utter_message(
                response='utter_pokemon_type',
                pokemon_name=pokemon_name,
                pokemon_type=pokemon_types[0],
            )
        else:
            dispatcher.utter_message(
                response='utter_pokemon_types',
                pokemon_name=pokemon_name,
                pokemon_types=", ".join(pokemon_types),
            )

        return []


class ActionListPokemonTypes(Action):
    """Action class for listing Pokémon types.

    It retrieves all Pokémon types from the Poke API.
    """

    def name(self) -> str:
        return 'action_list_pokemon_types'

    async def run(self, dispatcher: CollectingDispatcher, *args, **kwargs) -> list[dict[str, Any]]:
        try:
            pokemon_types = await retrieve_all_pokemon_types()
        except (ClientError, KeyError):
            logger.exception('Failed to list pokemon types.')
            dispatcher.utter_message(response='utter_pokeapi_error')
            return []

        pokemon_types = "\n".join(f"- {type_name.title()}" for type_name in pokemon_types)

        dispatcher.utter_message(
            response='utter_list_pokemon_types',
            pokemon_types=pokemon_types,
        )

        return []


class ActionPokemonCount(Action):
    """Action class for returning Pokémon count.

    It retrieves all Pokémon from the Poke API.
    """

    def name(self) -> str:
        return 'action_pokemon_count'

    async def run(self, dispatcher: CollectingDispatcher, *args, **kwargs) -> list[dict[str, Any]]:
        try:
            count = await pokemon_count()
        except (ClientError, KeyError):
            logger.exception('Failed to get pokemon count.')
            dispatcher.utter_message(response='utter_pokeapi_error')
            return []

        dispatcher.utter_message(
            response='utter_pokemon_count',
            count=count,
        )

        return []
