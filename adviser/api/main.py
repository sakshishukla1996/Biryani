from typing import Union
from fastapi import FastAPI

app = FastAPI()

data = {
    "stuttgart": {
        "indian": ["Indian palace", "Zayka", "Delhi Darbar"],
        "thai": ["Xing Ciao", "zhang Ziao"],
        "vietnamese": ["Acapella", "Grabing"],
        "mexican": ["el dorado", "jena penas", "jo papas"],
        "german": ["Apetite", "Kaufland", "Rewe"],
        "chinese": ["Asia wok", "Sichaun Cuisine", "King's palace"],
        "greek": ["alpha", "beta", "gamma"],
        "turkish": ["doner khana", "Durum khalo", "Samosa lelo"],
        "italian": ["Akhri pasta", "poora pizza", "Konda tiramisu"],
    },
    "berlin": {
        "indian": ["Berlin Indian palace", "Berlin Zayka", "Berlin Delhi Darbar"],
        "thai": ["Berlin Xing Ciao", "Berlin zhang Ziao"],
        "vietnamese": ["Berlin Acapella", "Berlin Grabing"],
        "mexican": ["Berlin el dorado", "Berlin jena penas", "Berlin jo papas"],
        "german": ["Berlin Apetite", "Berlin Kaufland", "Berlin Rewe"],
        "chinese": ["Berlin Asia wok", "Berlin Sichaun Cuisine", "Berlin King's palace"],
        "greek": ["Berlin alpha", "Berlin beta", "Berlin gamma"],
        "turkish": ["Berlin doner khana", "Berlin Durum khalo", "Berlin Samosa lelo"],
        "italian": ["Berlin Akhri pasta", "Berlin poora pizza", "Berlin Konda tiramisu"],
    },
}


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/location/{location}")
def read_item(location: str, cuisine: Union[str, None] = None):
    location = location if location in data.keys() else "stuttgart"
    cuisine = cuisine if cuisine in data[location].keys() else "indian"
    return {"location": location, "cuisine": cuisine, "restaurants": data[location][cuisine]}
