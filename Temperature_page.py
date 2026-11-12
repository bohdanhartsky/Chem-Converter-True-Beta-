
# conversions[from_unit][to_unit] = function that converts a value
conversions = {
    "celsius": {
        "celsius":    lambda c: c,
        "kelvin":     lambda c: c + 273.15,
        "fahrenheit": lambda c: c * 9 / 5 + 32,
    },
    "kelvin": {
        "celsius":    lambda k: k - 273.15,
        "kelvin":     lambda k: k,
        "fahrenheit": lambda k: (k - 273.15) * 9 / 5 + 32,
    },
    "fahrenheit": {
        "celsius":    lambda f: (f - 32) * 5 / 9,
        "kelvin":     lambda f: (f - 32) * 5 / 9 + 273.15,
        "fahrenheit": lambda f: f,
    },
}
 
def convert(value, from_unit, to_unit):
    return conversions[from_unit.lower()][to_unit.lower()](value)
 
if __name__ == "__main__":
    # The values from your screenshot should all agree
    print(convert(12, "Celsius", "Kelvin"))          # 285.15
    print(convert(12, "Celsius", "Fahrenheit"))      # 53.6
    print(convert(285.15, "Kelvin", "Celsius"))      # 12.0
    print(convert(285.15, "Kelvin", "Fahrenheit"))   # 53.6
    print(convert(53.6, "Fahrenheit", "Celsius"))    # 12.0
    print(convert(53.6, "Fahrenheit", "Kelvin"))     # 285.15
