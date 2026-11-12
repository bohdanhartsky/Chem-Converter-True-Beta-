import math
import random
from dataclasses import dataclass
from drafter import *

# Each of these files holds a dictionary of conversions and a convert() function.
# They must be saved in the same folder as this file.
import Length_Page
import Temperature_Page
import Area_Page
import Volume_Page
set_website_title("Chem Converter")
set_site_information(
    author="Bohdan Hartsky",
    description="Unit conversion.",
    sources="Thanks to the TA's that helped me with this.",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/bohdanhartsky/Chem-Converter-True-Beta"]
)
hide_debug_information()
set_website_framed(False)
 
# ---------------------------------------------------------------------------
# Conversion data (comes from the imported page files)
# ---------------------------------------------------------------------------
# The dictionary of units in each file, keyed by category
UNIT_TABLES = {
    "Length": Length_Page.conversions,
    "Temperature": Temperature_Page.conversions,
    "Area": Area_Page.area_conversions,
    "Volume": Volume_Page.conversions,
}
 
# The convert(value, from_unit, to_unit) function in each file
CONVERTERS = {
    "Length": Length_Page.convert,
    "Temperature": Temperature_Page.convert,
    "Area": Area_Page.convert,
    "Volume": Volume_Page.convert,
}
 
PUNS = [
    "I would tell you a chemistry joke, but I know I wouldn't get a reaction.",
    "Never trust atoms. They make up everything.",
    "If you're not part of the solution, you're part of the precipitate.",
    "Why do chemists like nitrates so much? They're cheaper than day rates.",
    "What did the scientist say when he found two isotopes of helium? HeHe.",
    "Helium walks into a bar. The bartender says, 'We don't serve noble gases here.' Helium doesn't react.",
    "A neutron walks into a bar and asks how much for a drink. The bartender says, 'For you, no charge.'",
]
 
 
# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class Symbol:
    index: int        # position of the unit in the list
    unit: str         # name of the unit, e.g. "Meter"
    category: str     # "Length", "Temperature", "Area" or "Volume"
 
 
@dataclass
class State:
    user_input: float          # the number the user typed
    units: list[Symbol]        # every unit the site knows about
    output: float              # the converted result
    convertible: bool          # False when the last conversion failed
    from_unit: str             # unit the user is converting from
    to_unit: str               # unit the user is converting into
    error: str                 # message describing the last error ("" if none)
    category: str              # which converter page the user is on
 
 
# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def build_units() -> list[Symbol]:
    """Make a Symbol for every unit in the imported dictionaries."""
    units = []
    for category, table in UNIT_TABLES.items():
        for name in table:
            units.append(Symbol(len(units), name.title(), category))
    return units
 
 
def find_symbol(units: list[Symbol], name: str):
    """Loop over the list of Symbols and return the one matching the name."""
    for symbol in units:
        if symbol.unit == name:
            return symbol
    return None
 
 
def calculate(value: float, source: Symbol, target: Symbol) -> float:
    """Convert value using the imported convert() function for its category."""
    convert = CONVERTERS[source.category]
    if source.category == "Temperature":
        kelvin = convert(value, source.unit, "Kelvin")
        if kelvin < -1e-9:
            raise ValueError(
                f"{value:g} {source.unit} is below absolute zero, "
                "which is the lowest possible temperature."
            )
    return convert(value, source.unit, target.unit)
 
 
def fmt(number: float) -> str:
    """Show a number with up to 10 significant digits."""
    return f"{number:.10g}"
 
 
# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
DEFAULT_UNITS = {
    "Length": ("Meter", "Kilometer"),
    "Temperature": ("Celsius", "Kelvin"),
    "Area": ("Square Meter", "Square Kilometer"),
    "Volume": ("Liter", "Milliliter"),
}
 
 
@route
def index(state: State) -> Page:
    """Main page: choose which kind of unit to convert."""
    return Page(state, [
        Header("Unit Converter"),
        "What would you like to convert?",
        Button("Length", length_page),
        Button("Temperature", temperature_page),
        Button("Area", area_page),
        Button("Volume", volume_page),
        HorizontalRule(),
        Link(".", secret_page),   # the well-hidden Easter egg link
    ])
 
 
def converter_page(state: State, category: str) -> Page:
    """Builds the converter page for one category of units."""
    state.category = category
 
    # Loop over state.units to collect only this category's unit names
    names = []
    for symbol in state.units:
        if symbol.category == category:
            names.append(symbol.unit)
 
    # If the saved selection belongs to a different category, reset it
    default_from, default_to = DEFAULT_UNITS[category]
    if state.from_unit not in names:
        state.from_unit = default_from
    if state.to_unit not in names:
        state.to_unit = default_to
 
    return Page(state, [
        Header(f"{category} Converter"),
        "Enter a number, then choose the unit you have and the unit you want.",
        TextBox("number", fmt(state.user_input)),
        "Convert from:",
        SelectBox("from_unit", names, state.from_unit),
        "Convert into:",
        SelectBox("to_unit", names, state.to_unit),
        LineBreak(),
        Button("Convert", convert_units),
        HorizontalRule(),
        Button("Back to main page", index),
    ])
 
 
@route
def length_page(state: State) -> Page:
    return converter_page(state, "Length")
 
 
@route
def temperature_page(state: State) -> Page:
    return converter_page(state, "Temperature")
 
 
@route
def area_page(state: State) -> Page:
    return converter_page(state, "Area")
 
 
@route
def volume_page(state: State) -> Page:
    return converter_page(state, "Volume")
 
 
# Lets other pages send the user back to the converter they were using
CATEGORY_PAGES = {
    "Length": length_page,
    "Temperature": temperature_page,
    "Area": area_page,
    "Volume": volume_page,
}
 
 
@route
def convert_units(state: State, number: str, from_unit: str, to_unit: str) -> Page:
    """Checks the input, converts, and sends the user to the right page."""
    state.from_unit = from_unit
    state.to_unit = to_unit
    state.error = ""
    state.convertible = True
 
    # 1) Is the number valid?
    try:
        value = float(number)
    except ValueError:
        value = None
    if value is None or not math.isfinite(value):
        state.convertible = False
        state.error = f'"{number}" is not a valid number. Enter digits only, like 12 or 3.5.'
        return invalid_input_page(state)
    state.user_input = value
 
    # 2) Find the chosen units by looping through state.units
    source = find_symbol(state.units, from_unit)
    target = find_symbol(state.units, to_unit)
    if source is None or target is None:
        state.convertible = False
        state.error = "One of the selected units was not recognized."
        return error_page(state)
 
    # 3) Do the conversion
    try:
        state.output = calculate(value, source, target)
    except ValueError as problem:
        state.convertible = False
        state.error = str(problem)
        return invalid_input_page(state)
 
    return output_page(state)
 
 
@route
def output_page(state: State) -> Page:
    """Shows the successful conversion."""
    return Page(state, [
        Header("Result"),
        f"{fmt(state.user_input)} {state.from_unit} = {fmt(state.output)} {state.to_unit}",
        LineBreak(),
        Button("Convert another", CATEGORY_PAGES[state.category]),
        Button("Back to main page", index),
    ])
 
 
@route
def invalid_input_page(state: State) -> Page:
    """The input could not be used."""
    return Page(state, [
        Header("Invalid Input"),
        "That input couldn't be used for a conversion.",
        Button("Try again", CATEGORY_PAGES[state.category]),
        Button("Back to main page", index),
        Button("See what went wrong", error_page),
    ])
 
 
@route
def error_page(state: State) -> Page:
    """Lists the error that caused the problem."""
    if state.error == "":
        message = "There is no error to show."
    else:
        message = state.error
    return Page(state, [
        Header("Error Details"),
        message,
        Button("Try again", CATEGORY_PAGES[state.category]),
        Button("Back to main page", index),
    ])
 
 
@route
def secret_page(state: State) -> Page:
    """Easter egg: a random chemistry pun."""
    return Page(state, [
        Header("You found the secret page!"),
        random.choice(PUNS),
        Button("Back to home", index),
    ])
 
 
start_server(State(1.0, build_units(), 0.0, True, "Meter", "Kilometer", "", "Length"))
