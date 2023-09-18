from __future__ import annotations

import aiohttp

POKEMON_API = 'https://pokeapi.co/api/v2/'
POKEMON_ENDPOINT = f'{POKEMON_API}pokemon/'
POKEMON_TYPES_ENDPOINT = f'{POKEMON_API}type/'


class PokemonNotFound(Exception):
    """Exception raised when a Pokémon is not found."""

    def __init__(self, pokemon_name: str) -> None:
        self.pokemon_name = pokemon_name
        super().__init__(f"Pokemon '{pokemon_name}' not found.")


async def check_pokemon_existence(pokemon_name: str) -> bool:
    """Check the existence of a Pokémon in Poke API."""
    async with aiohttp.ClientSession() as session:
        async with session.head(f'{POKEMON_ENDPOINT}{pokemon_name.lower()}') as resp:
            resp.raise_for_status()
            return resp.ok


async def retrieve_pokemon_data(pokemon_name: str) -> dict:
    """Retrieve data from Poke API for a Pokémon."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{POKEMON_ENDPOINT}{pokemon_name.lower()}') as resp:
            if resp.status == 404:
                raise PokemonNotFound(pokemon_name)

            resp.raise_for_status()

            return await resp.json()


async def retrieve_all_pokemon_types_data() -> dict:
    """Retrieve data for all Pokémon types from Poke API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(POKEMON_TYPES_ENDPOINT) as resp:
            resp.raise_for_status()
            return await resp.json()


async def pokemon_count() -> int:
    """Get the count of total Pokémon from Poke API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(POKEMON_ENDPOINT, params={'limit': 1}) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data['count']


async def verify_pokemon_type(pokemon_name: str, pokemon_type: str) -> bool:
    """Verify the type of a Pokémon in Poke API."""
    data = await retrieve_pokemon_data(pokemon_name)

    pokemon_type = pokemon_type.lower()
    return any(pokemon_type == slot['type']['name'] for slot in data['types'])


async def retrieve_pokemon_types(pokemon_name: str) -> list[str]:
    """Retrieve the types of a Pokémon from Poke API."""
    data = await retrieve_pokemon_data(pokemon_name)

    return [slot['type']['name'] for slot in data['types']]


async def retrieve_all_pokemon_types() -> list[str]:
    """Retrieve all Pokémon types from Poke API."""
    data = await retrieve_all_pokemon_types_data()

    return [slot['name'] for slot in data['results']]
