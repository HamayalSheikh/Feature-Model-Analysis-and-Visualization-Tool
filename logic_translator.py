def translate_to_logic(feature, parent_name=None, logic=None):
    """
    Translates the feature model into a propositional logic formula with structured formatting.

    Args:
        feature (Feature): The current feature being processed.
        parent_name (str): The name of the parent feature.
        logic (dict): A dictionary to hold categorized propositional logic.

    Returns:
        dict: A dictionary containing propositional logic formulas organized by categories.
    """
    if logic is None:
        # Initialize the logic dictionary with categories
        logic = {
            "root": [],
            "mandatory": [],
            "children_to_parent": [],
            "xor": [],
            "or": [],
            "constraints": [],
        }

    # Add root feature logic
    if parent_name is None:
        logic["root"].append(f"{feature.name}")

    # Process child features
    for child in feature.children:
        # Mandatory relationships
        if child.mandatory:
            logic["mandatory"].append(f"{feature.name} -> {child.name}")
            logic["children_to_parent"].append(f"{child.name} -> {feature.name}")
        else:
            logic["children_to_parent"].append(f"{child.name} -> {feature.name}")

        # OR Group
        if child.group_type == "or":
            or_logic = " | ".join(c.name for c in child.children)
            logic["or"].append(f"{child.name} -> ({or_logic})")

        # XOR Group
        if child.group_type == "xor":
            xor_logic = " | ".join(
                f"({a.name} & " + " & ".join(f"!{b.name}" for b in child.children if b != a) + ")"
                for a in child.children
            )
            logic["xor"].append(f"{child.name} -> ({xor_logic})")

        # Recurse for child features
        translate_to_logic(child, feature.name, logic)

    return logic


def format_and_print_logic(logic):
    """
    Formats and prints the categorized propositional logic.

    Args:
        logic (dict): A dictionary containing categorized propositional logic formulas.
    """
    print("//root")
    print(" &\n".join(logic["root"]) + " &")

    print("\n//mandatory children")
    print(" &\n".join(logic["mandatory"]) + " &")

    print("\n//children -> parent")
    print(" &\n".join(logic["children_to_parent"]) + " &")

    print("\n//xor")
    print(" &\n".join(logic["xor"]) + " &")

    print("\n//or")
    print(" &\n".join(logic["or"]) + " &")


    print("\n//constraints")
    print(" &\n".join(logic["constraints"]))

    
