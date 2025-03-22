from flask import Flask, request, render_template
from requests.exceptions import RequestException
from requests import get
from easygui import enterbox, ynbox, msgbox
from PIL import Image
from tempfile import NamedTemporaryFile
from io import BytesIO
from random import randint

app = Flask(__name__)

def getImage(imageURL, size=(256, 256)):
    response = get(imageURL)
    if response.status_code == 200:
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes)

        image.thumbnail(size)

        temp_file = NamedTemporaryFile(delete=True, suffix=".png")
        temp_file.close()
        image.save(temp_file.name)

        return temp_file.name

    return None

def getPokemonData(pokemonName):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemonName.lower()}"
    try:
        response = get(url)
        if response.status_code == 200:
            pokemon_data = response.json()
            return pokemon_data
        else:
            retry = ynbox("Pokémon data not found. Do you want to retry?", "Retry?", ("Retry", "Exit"))
            if retry:
                getPokemonData(pokemonName)
            
    except RequestException as e:
        msgbox(f"Error: {e}")
        return None

def getGeneration(pokemon_species_url):
    response = get(pokemon_species_url)
    if response.status_code == 200:
        species_data = response.json()
        generation_data = species_data.get("generation", {})
        generation_name = generation_data.get("name", "Unknown")
        if generation_name.startswith("generation-"):
            generation_number = generation_name.split("-")[-1]
            return f"Generation {generation_number}"
    return "Unknown"

@app.route('/', methods=['GET', 'POST'])
def index():
    title = "PokeApiLinobo"
    msg = "Find Pokémon by name or ID"
    imageURL = "https://i.imgur.com/g8yYrvY.png"

    if request.method == 'POST':
        pokemonName = request.form.get('pokemon_name')
        data = getPokemonData(pokemonName)
        if data:
            species_url = data["species"]["url"]
            generation = getGeneration(species_url)

            msg = (
                f"ID: {data['id']}.\n"
                f"Name: {data['name']}.\n"
                f"Abilities: {', '.join([ability['ability']['name'] for ability in data['abilities']])}.\n"
                f"Types: {', '.join([type_data['type']['name'] for type_data in data['types']])}.\n"
                f"Movements: {', '.join([move_data['move']['name'] for move_data in data['moves'][-4:]])}.\n"
                f"Generation: {generation}\n"
            )

            imageURL = data["sprites"]["other"]["official-artwork"]["front_default"]
            return render_template('index.html', msg=msg, imageURL=imageURL)

    return render_template('index.html', title=title, msg=msg, imageURL=imageURL)

if __name__ == "__main__":
    app.run(debug=True)
