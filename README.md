# Poke Chat Bot and Pokédex Web Application

This project combines a chat bot for Pokémon-related queries using Rasa and a web application featuring a Pokédex and
a list page for berries.
The web application is built using Django and includes a chat bot widget for easy access to the chat bot functionality.
It utilizes HTMX for dynamic content loading and updates, and Tailwind CSS for styling.

## Features

- Interactive chat bot powered by Rasa to answer Pokémon-related queries.
- Pokédex page with detailed information about various Pokémon.
- List page showcasing different types of berries.
- Smooth and responsive experience akin to a Single Page Application.

## Running Locally

### Create env files

Local environment files should be located in `./.envs/` directory.

Needed environment files:

- **.django**
- **.postgres**

Examples of these environment files are available in the same directory.

### Build the Stack

Builds the Docker containers for the local development environment.

```sh
docker-compose build
```

### Run the Stack

```sh
docker compose up
```

To run in a detached (background) mode

```sh
docker compose up -d
```

### Train model

```sh
docker-compose run --rm rasa train --fixed-model-name model
```

## Technologies

- [Docker](https://www.docker.com/)
- [django](https://www.djangoproject.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Rasa](https://rasa.com/)
- [htmx](https://htmx.org/)
- [Alpine.js](https://alpinejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
