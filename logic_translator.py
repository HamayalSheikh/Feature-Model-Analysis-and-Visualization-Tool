def translate_to_logic(feature, parent_name=None, logic=None):
    if logic is None:
        logic = {"root": [], "mandatory": [], "children_to_parent": [], "xor": [], "or": [], "constraints": []}

    if parent_name is None:
        logic["root"].append(f"{feature.name}")

    for child in feature.children:
        if child.mandatory:
            logic["mandatory"].append(f"{feature.name} -> {child.name}")
            logic["children_to_parent"].append(f"{child.name} -> {feature.name}")
        else:
            logic["children_to_parent"].append(f"{child.name} -> {feature.name}")

        if child.group_type == "or" and child.children:
            or_logic = " | ".join(c.name for c in child.children)
            logic["or"].append(f"{child.name} -> ({or_logic})")

        if child.group_type == "xor" and child.children:
            xor_logic = " | ".join(
                f"({a.name} & " + " & ".join(f"!{b.name}" for b in child.children if b != a) + ")"
                for a in child.children
            )
            logic["xor"].append(f"{child.name} -> ({xor_logic})")

        translate_to_logic(child, feature.name, logic)

    return logic


def format_and_print_logic(logic):
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
    print(" &\n".join(logic["constraints"]) + " &")
