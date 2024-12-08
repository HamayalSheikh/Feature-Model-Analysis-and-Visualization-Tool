import React, { useState, useEffect, useCallback } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckSquare, faSquare, faFolder, faFolderOpen, faChevronDown, faChevronRight } from "@fortawesome/free-solid-svg-icons";

const FeatureTree = () => {
    const [checked, setChecked] = useState([]);
    const [expanded, setExpanded] = useState([]);
    const [treeData, setTreeData] = useState([]);
    const [constraints, setConstraints] = useState([]);
    const [logic, setLogic] = useState([]);
    const [mwp, setMwp] = useState([]);

    const xmlData = "feature_model.xml"

    // Format tree data from backend response
    const formatTreeData = useCallback((features) => {
        const processNode = (node, parent = null) => {
            let type = ""

            if (node.label.includes("(xor")) {
                type = "xor"
            } else if (node.label.includes("(or")) {
                type = "or"
            }

            const formattedNode = {
                label: node.label,
                value: node.value,
                mandatory: node.mandatory || false,
                groupType: type,
                parent: parent
            };

            // Process children recursively
            if (node.children && node.children.length > 0) {
                formattedNode.children = node.children.map(child => processNode(child, formattedNode));
            }

            return formattedNode;
        };

        return features.map(processNode);
    }, []);

    // Fetch data from backend (remains the same as in previous version)
    useEffect(() => {
        if (!xmlData) return;
    
        fetch("http://127.0.0.1:5000/parse-xml", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ xml: xmlData }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Error fetching XML data: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Received data:", data);
    
                if (!data.treeData || typeof data.treeData !== "object" || !data.treeData.children) {
                    console.error("Invalid or missing 'treeData' in response:", data);
                    setTreeData([]);
                    return;
                }
    
                const formattedTreeData = formatTreeData([data.treeData]);
                setTreeData(formattedTreeData);
    
                const formattedConstraints = Array.isArray(data.constraints)
                    ? data.constraints
                    : [];
                setConstraints(formattedConstraints);
            })
            .catch((error) => console.error("Error fetching XML data:", error));

            fetch("http://127.0.0.1:5000/getData", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ xml: xmlData }),
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Error fetching XML data: ${response.statusText}`);
                    }
                    return response.json(); // Parse the JSON response
                })
                .then((data) => {
                    console.log("Received data:", data);
            
                    // Check if "logic" exists and is a valid array
                    if (!data.logic || typeof data.logic !== "object") {
                        console.error("Invalid or missing 'logic' in response:", data);
                        setLogic([]); // Reset logic state if invalid
                        return;
                    }
            
                    const formattedLogic = Array.isArray(data.logic) ? data.logic : [];
                    setLogic(formattedLogic); // Update state with formatted logic
                })
                .catch((error) => {
                    console.error("Error fetching data:", error.message);
                });
            
    }, [xmlData, formatTreeData]);

    const handleCheck = (value, isChecked) => {
        const rootNode = treeData[0];
        let updatedChecked = [...checked];

        const updateNodeSelection = (node, isSelecting) => {
            // Special handling for root node
            if (node.value === rootNode.value && !isSelecting) {
                updatedChecked = [];
                return;
            }

            if(isSelecting) {
                if(node.mandatory) {
                    updatedChecked = findMandatoryNodes(rootNode);
                    updatedChecked.push(node.value);
                    updatedChecked.push(node.parent.value);
                    if(!updatedChecked.includes(rootNode.value)) {
                        updatedChecked.push(rootNode.value);
                    }
                    return;
                }
            }

            if(!isSelecting) {
                //check if node is mandatory
                if(node.mandatory) {
                    updatedChecked = []
                    return;
                }
            }

            // If selecting root, only select mandatory nodes
            if (node.value === rootNode.value && isSelecting) {
                updatedChecked = findMandatoryNodes(node);
                updatedChecked.push(node.value);
                
                return;
            }

            // Handle XOR constraint
            if (node.parent?.groupType === "xor") {
                if (isSelecting) {
                    // Deselect other siblings in XOR group
                    node.parent.children.forEach(sibling => {
                        if (sibling.value !== node.value) {
                            updatedChecked = updatedChecked.filter(v => v !== sibling.value);
                        }
                    });
                }
            }

            // Add or remove the current node
            if (isSelecting) {
                if (!updatedChecked.includes(node.value)) {
                    updatedChecked.push(node.value);
                }

                // Select mandatory parent nodes
                let currentParent = node.parent;
                while (currentParent) {
                    if (currentParent.mandatory && !updatedChecked.includes(currentParent.value)) {
                        updatedChecked.push(currentParent.value);
                    }
                    currentParent = currentParent.parent;
                }

                // Select node's mandatory children
                if (node.children) {
                    node.children.forEach(child => {
                        if (child.mandatory && !updatedChecked.includes(child.value)) {
                            updatedChecked.push(child.value);
                        }
                    });
                }
            } else {
                // Deselection logic
                updatedChecked = updatedChecked.filter(v => v !== node.value);

                // Check if parent needs to be deselected
                if (node.parent) {
                    const allChildrenDeselected = node.parent.children.every(
                        child => !updatedChecked.includes(child.value)
                    );
                    if (allChildrenDeselected) {
                        updatedChecked = updatedChecked.filter(v => v !== node.parent.value);
                    }
                }
            }
        };

        // Find mandatory nodes recursively
        const findMandatoryNodes = (node) => {
            const mandatoryNodes = [];
            
            const traverse = (currentNode) => {
                if (currentNode.mandatory) {
                    mandatoryNodes.push(currentNode.value);
                }
                
                if (currentNode.children) {
                    currentNode.children.forEach(traverse);
                }
            };

            traverse(node);
            return mandatoryNodes;
        };

        // Find the target node
        const targetNode = findFeatureByValue(value, rootNode);
        
        if (targetNode) {
            updateNodeSelection(targetNode, isChecked);
        }

        // Ensure uniqueness and update state
        setChecked([...new Set(updatedChecked)]);
    };

    // Existing helper functions remain the same
    const findFeatureByValue = (value, node) => {
        if (node.value === value) return node;
        for (const child of node.children || []) {
            const found = findFeatureByValue(value, child);
            if (found) return found;
        }
        return null;
    };

    const findParentFeature = (value, node) => {
        if (node.children) {
            for (const child of node.children) {
                if (child.value === value) return node;
                const parent = findParentFeature(value, child);
                if (parent) return parent;
            }
        }
        return null;
    };

    // Expand/collapse functionality
    const handleExpand = (value) => {
        setExpanded(prev =>
            prev.includes(value)
                ? prev.filter(v => v !== value)
                : [...prev, value]
        );
    };

    // Render icon functions
    const renderFolderIcon = (mandatory) => {
        return mandatory
            ? <FontAwesomeIcon icon={faFolderOpen} style={{ color: "red" }} />
            : <FontAwesomeIcon icon={faFolder} />;
    };

    const renderExpandCollapseIcon = (value, node) => {
        // Only render expand/collapse icon if node has children
        if (!node.children || node.children.length === 0) return null;

        return expanded.includes(value)
            ? <FontAwesomeIcon icon={faChevronDown} />
            : <FontAwesomeIcon icon={faChevronRight} />;
    };

    const renderIcon = (value) => {
        return checked.includes(value)
            ? <FontAwesomeIcon icon={faCheckSquare} />
            : <FontAwesomeIcon icon={faSquare} />;
    };

    // Render tree nodes
    const renderNode = (node) => {
        return (
            <div style={{marginLeft: "5px"}}key={node.value}>
                <div style={{ display: "flex", alignItems: "center", margin: "5px 0" }}>
                    {/* Folder Expand Icon */}
                    {node.children && node.children.length > 0 && (
                        <div
                            onClick={() => handleExpand(node.value)}
                            style={{ cursor: "pointer", marginRight: "5px" }}
                        >
                            {renderExpandCollapseIcon(node.value, node)}
                        </div>
                    )}

                    {/* Checkbox and Folder Icon */}
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            cursor: "pointer"
                        }}
                        onClick={() => handleCheck(node.value, !checked.includes(node.value))}
                    >
                        <div style={{ marginRight: "10px" }}>
                            {renderIcon(node.value)}
                        </div>
                        <div>{renderFolderIcon(node.mandatory)}</div>
                        <div style={{
                            marginLeft: "10px",
                            fontWeight: node.mandatory ? "bold" : "normal"
                        }}>
                            {node.label}
                        </div>
                    </div>
                </div>

                {/* Render Child Nodes */}
                {node.children && node.children.length > 0 && expanded.includes(node.value) && (
                    <div style={{ paddingLeft: "20px" }}>
                        {node.children.map((child) => renderNode(child))}
                    </div>
                )}
            </div>
        );
    };

    // Render nothing if no tree data
    if (treeData.length === 0) {
        return <div>Loading...</div>;
    }

    return (
        
        <div>
            <h1>Feature Model</h1>
            {console.log("treeData", treeData)}
            {treeData.map((rootNode) => renderNode(rootNode))}

            <h1>Constraints</h1>
            <pre>{JSON.stringify(constraints, null, 2)}</pre>

            <h1>Logic</h1>
            <pre>{JSON.stringify(logic, null, 2)}</pre>

            <h1>Checked</h1>
            <pre>{JSON.stringify(checked, null, 2)}</pre>
        </div>
    );
};

export default FeatureTree;

