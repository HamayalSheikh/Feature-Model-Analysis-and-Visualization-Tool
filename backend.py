from flask import Flask, jsonify, request
from flask_cors import CORS
from xml.etree.ElementTree import ParseError
from xml_parser import load_and_parse_xml, parse_constraints

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/parse-xml', methods=['POST'])
def parse_xml():
    try:
        # Get the XML data from the request
        xml_data = request.json.get("xml")
        temp_file = "feature_model_temp.xml"

        # Write XML to a temporary file for parsing
        with open(temp_file, "w") as file:
            file.write(xml_data)

        # Parse the XML and constraints
        root, root_feature = load_and_parse_xml(temp_file)
        constraints = parse_constraints(root)

        def feature_to_dict(feature):
            """
            Convert the Feature object to a dictionary for serialization.
            """
            return {
                "label": feature.name,
                "value": feature.name,
                "groupType": feature.group_type,
                "mandatory": feature.mandatory,
                "children": [feature_to_dict(child) for child in feature.children]
            }

        # Convert the root feature to a dictionary
        feature_model = feature_to_dict(root_feature)

        return jsonify({
            "treeData": feature_model,
            "constraints": constraints
        })

    except ParseError as e:
        return jsonify({"error": "Invalid XML file", "details": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    

@app.route('/validate-configuration', methods=['POST'])
def validate_configuration():
    data = request.json

    # Extract the fields from the incoming JSON
    mandatory_nodes = data.get("mandatory")
    or_groups = data.get("or")
    xor_groups = data.get("xor")
    and_groups = data.get("and")
    selected_nodes = data.get("selected")
    
    # Print the data for debugging
    print("Mandatory Nodes:", mandatory_nodes)
    print("OR Groups:", or_groups)
    print("XOR Groups:", xor_groups)
    print("AND Groups:", and_groups)
    print("Selected Nodes:", selected_nodes)
    # print("x")

    validation_result = validate_tree_configuration(mandatory_nodes, or_groups, xor_groups, and_groups, selected_nodes)
    
    pass

    return jsonify(validation_result)
    # return jsonify({"isValid": True, "messages": []})

def validate_tree_configuration(mandatory_nodes, or_groups, xor_groups, and_groups, selected_nodes):
    
    result = {"isValid": True, "messages": []}

    # Check for missing mandatory nodes
    selected_Mandatory = selected_nodes.get('mandatory', {})
    for node in selected_Mandatory.values():
        if node not in mandatory_nodes:
            result['isValid'] = False
            result['messages'].append(f"Missing mandatory node: {node}")
    
    # Validate OR groups
    # get or groups from selected nodes
    selected_OR = selected_nodes.get('or', {})
    for node in or_groups:
        if node not in selected_OR:
            result['isValid'] = False
            result['messages'].append(f"Invalid OR group: {node} requires one child to be selected.")
        print(result['messages'])
        
    
    # Validate XOR groups
    selected_XOR = selected_nodes.get('xor', {})
    for node in selected_XOR:
        if node not in xor_groups:
            result['isValid'] = False
            result['messages'].append(f"Invalid XOR group: {node} requires one child to be selected.")
        if len(selected_XOR[node]) != 1:
            result['isValid'] = False
            result['messages'].append(f"Invalid XOR group: {node} requires exactly one child to be selected.")
        print(result['messages'])
        
    
    # Validate AND groups
    selected_AND = selected_nodes.get('and', {})
    for node in and_groups:
        if node not in selected_AND:
            result['isValid'] = False
            result['messages'].append(f"Invalid AND group: {node} requires all children to be selected.")
        print(result['messages'])

    return result


if __name__ == '__main__':
    app.run(debug=True)



