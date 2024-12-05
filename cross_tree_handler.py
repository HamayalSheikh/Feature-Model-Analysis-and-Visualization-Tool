def handle_cross_tree_constraints(constraints, feature_names):
    """
    Translates cross-tree constraints into logic.

    Args:
        constraints (list): List of constraints in natural language.
        feature_names (set): Set of feature names to use in the logic.

    Returns:
        list: A list of constraints formatted for logic evaluation.
    """
    translated_constraints = []
    for constraint in constraints:
        if "requires" in constraint:
            feature_a, feature_b = constraint.split("requires")
            # Extract only feature names
            feature_a = extract_feature_name(feature_a.strip(), feature_names)
            feature_b = extract_feature_name(feature_b.strip(), feature_names)
            translated_constraints.append(f"{feature_a} -> {feature_b}")
        elif "excludes" in constraint:
            feature_a, feature_b = constraint.split("excludes")
            # Extract only feature names
            feature_a = extract_feature_name(feature_a.strip(), feature_names)
            feature_b = extract_feature_name(feature_b.strip(), feature_names)
            translated_constraints.append(f"!{feature_a} | !{feature_b}")
        elif "is required to" in constraint:  # Handle 'is required to'
            feature_a, feature_b = constraint.split("is required to")
            # Extract only feature names
            feature_a = extract_feature_name(feature_a.strip(), feature_names)
            feature_b = extract_feature_name(feature_b.strip(), feature_names)
            translated_constraints.append(f"{feature_a} -> {feature_b}")
    return translated_constraints

def extract_feature_name(feature):
    """
    Recursively extracts all feature names from the feature model.

    Args:
        feature (Feature): The root feature of the model.

    Returns:
        set: A set of feature names.
    """
    feature_names = {feature.name}
    for child in feature.children:
        feature_names.update(extract_feature_name(child))
    return feature_names

