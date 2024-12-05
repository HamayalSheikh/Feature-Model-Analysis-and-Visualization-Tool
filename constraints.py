def validate_constraints(feature_model):
    """
    Validates the feature model constraints.
    Raises exceptions for invalid configurations.
    """
    if not feature_model.mandatory:
        raise Exception(f"Mandatory feature '{feature_model.name}' cannot be disabled!")

    for child in feature_model.children:
        validate_constraints(child)

    # Cross-tree constraints
    filtered = next((f for f in feature_model.children if f.name == "Catalog"), None)
    location = next((f for f in feature_model.children if f.name == "Location"), None)

    if filtered:
        by_location = any(c.name == "ByLocation" for c in filtered.children)
        if by_location and not location:
            raise Exception("Location feature is required for ByLocation filtering!")


def validate_xor_group(features):
    """
    Validates that only one feature in an XOR group is selected.
    """
    selected = [feature for feature in features if feature.mandatory]
    if len(selected) > 1:
        raise Exception("Only one feature can be selected in an XOR group!")
    return True
