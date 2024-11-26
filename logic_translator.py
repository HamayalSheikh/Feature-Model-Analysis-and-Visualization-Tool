# Converts feature model to propositional logic

def translate_to_logic(xml_data):
    # Parse features and translate them to logic
    logic = []
    for feature in xml_data.findall(".//feature"):
        feature_name = feature.get("name")
        logic.append(f"{feature_name}")  # Add logic rules here
    return logic

