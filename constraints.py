# Verifies feature selections and checks constraints

# def check_constraints(selections, constraints):
#     for constraint in constraints:
#         if not eval(constraint):
#             return False, constraint  # Return invalid constraint
#     return True, None

def validate_constraints(feature_model):
    """
    Validates the feature model constraints.
    Raises exceptions for invalid configurations.
    """
    # Mandatory feature validation
    if not feature_model.mandatory:
        raise Exception(f"Mandatory feature '{feature_model.name}' cannot be disabled!")

    for child in feature_model.children:
        validate_constraints(child)

    # Cross-tree constraints
    # Example: Location is required for ByLocation filtering
    filtered = next((f for f in feature_model.children if f.name == "Catalog"), None)
    location = next((f for f in feature_model.children if f.name == "Location"), None)

    if filtered:
        by_location = any(c.name == "ByLocation" for c in filtered.children)
        if by_location and not location:
            raise Exception("Location feature is required for ByLocation filtering!")
