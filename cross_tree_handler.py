 # Handles cross-tree constraints translation

def handle_cross_tree_constraints(constraints):
    translated_constraints = []
    for constraint in constraints:
        if "requires" in constraint:
            feature_a, feature_b = constraint.split("requires")
            translated_constraints.append(f"{feature_a.strip()} → {feature_b.strip()}")
    return translated_constraints


