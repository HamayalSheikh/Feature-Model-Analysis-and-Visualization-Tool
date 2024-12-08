import React, { useState, useEffect, useCallback } from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faCheckSquare,
    faSquare,
    faFolder,
    faFolderOpen,
    faChevronDown,
    faChevronRight,
} from "@fortawesome/free-solid-svg-icons";
import { counter } from "@fortawesome/fontawesome-svg-core";

const Container = styled.div`
    font-family: Arial, sans-serif;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
`;

const Title = styled.h1`
    text-align: center;
    color: #2c3e50;
    margin-bottom: 20px;
`;

const FileUploadWrapper = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;

    input[type="file"] {
        border: 2px dashed #95a5a6;
        border-radius: 5px;
        padding: 10px;
        width: 100%;
        max-width: 400px;
        margin-top: 10px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
            border-color: #3498db;
        }
    }
`;

const ErrorMessage = styled.p`
    color: red;
    font-weight: bold;
`;

const TreeWrapper = styled.div`
    border: 1px solid #bdc3c7;
    border-radius: 5px;
    padding: 10px;
    background-color: #ecf0f1;
    max-height: 600px;
    overflow-y: auto;
`;

const Node = styled.div`
    display: flex;
    align-items: center;
    margin: 5px 0;
    padding: 5px;
    background-color: ${(props) => (props.mandatory === "true" ? "#f39c12" : "transparent")};
    border-radius: 5px;

    &:hover {
        background-color: ${(props) => (props.mandatory === "true" ? "#e67e22" : "#dfe6e9")};
        cursor: pointer;
    }
`;


const NodeLabel = styled.div`
    margin-left: 10px;
    font-weight: ${(props) => (props.mandatory ? "bold" : "normal")};
`;

const FolderIconWrapper = styled.div`
    margin-right: 10px;
    display: flex;
    align-items: center;
`;

const ExpandIconWrapper = styled.div`
    margin-right: 5px;
    cursor: pointer;
`;

const FeatureTree = () => {
    const [checked, setChecked] = useState([]);
    const [expanded, setExpanded] = useState([]);
    const [treeData, setTreeData] = useState([]);
    const [constraints, setConstraints] = useState([]);
    const [error, setError] = useState(null);
    const [checkXOR, setCheckXOR] = useState(false);
    const [english, setEnglish] = useState(false);
    const [propositionalLogic, setPropositionalLogic] = useState(false);

    const formatTreeData = useCallback((features) => {
        const processNode = (node, parent = null) => {
            let type = "";

            if (node.label.includes("-xor")) {
                type = "xor";
            } else if (node.label.includes("-or")) {
                type = "or";
            } else if (node.label.includes("-and")) {
                type = "and";
            }

            const formattedNode = {
                label: node.label,
                value: node.value,
                mandatory: node.mandatory || false,
                groupType: type,
                parent: parent,
            };

            if (node.children && node.children.length > 0) {
                formattedNode.children = node.children.map((child) =>
                    processNode(child, formattedNode)
                );
            }

            return formattedNode;
        };

        return features.map(processNode);
    }, []);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const xmlContent = e.target.result;

            fetch("http://127.0.0.1:5000/parse-xml", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ xml: xmlContent }),
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Error fetching XML data: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    if (!data.treeData || typeof data.treeData !== "object" || !data.treeData.children) {
                        setTreeData([]);
                        setError("Invalid tree data received.");
                        return;
                    }

                    const formattedTreeData = formatTreeData([data.treeData]);
                    setTreeData(formattedTreeData);
                    const formattedConstraints = Array.isArray(data.constraints)
                        ? data.constraints
                        : [];
                    setConstraints(formattedConstraints);
                    setError(null);
                })
                .catch((err) => setError(`Failed to upload XML: ${err.message}`));
        };

        reader.readAsText(file);
    };

    const validateSelection = async () => {
        // Prepare the validation payload
        const payload = prepareValidationPayload();

        const validationPayload = {
            mandatory: payload.mandatory || [],
            or: payload.or || {},
            xor: payload.xor || {},
            and: payload.and || {},
            selected: payload.selected || {},
        };

        // Log the payload to check if it's properly formed
        console.log("tree:", payload.tree);
        console.log("Validation Payload:", validationPayload);

        try {
            // Send the validation request to the backend
            const response = await fetch("http://127.0.0.1:5000/validate-configuration", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(validationPayload),
            });

            // Check if the response is valid
            if (!response.ok) {
                throw new Error(`Validation failed: ${response.statusText}`);
            }

            // Process the response from the backend
            const result = await response.json();

            if (result.isValid) {
                alert("Configuration is valid!");
            } else {
                alert(`Invalid configuration: ${result.error}`);
            }
        } catch (error) {
            // Catch and display any errors
            console.error("Error validating selection:", error.message);
            alert("Failed to validate the configuration. Please try again.");
        }
    };

    const translate = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5000/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ prompt: english }),
            });
            if (!response.ok) {
                throw new Error(`Translation failed: ${response.statusText}`);
            }
            const result = await response.json();
            console.log(result);
            setPropositionalLogic(result);
        }
        catch (error) {
            console.error("Error translating:", error.message);
            alert("Failed to translate the configuration. Please try again.");
        }
    };


    const prepareValidationPayload = () => {
        const mandatoryNodes = [];
        const orGroups = {};
        const xorGroups = {};
        const andGroups = {};

        // Helper function to recursively process tree nodes
        const traverseTree = (node) => {
            if (node.mandatory) {
                mandatoryNodes.push(node.value);
            }
            if (node.groupType === "or") {
                if (!orGroups[node.parent?.value]) {
                    orGroups[node.parent?.value] = [];
                }
                // orGroups[node.parent.value].push(node.value);
                if (node.children) {
                    node.children.forEach(child => {
                        orGroups[node.parent.value].push(child.value);
                    });
                }
            }
            if (node.groupType === "xor") {
                if (!xorGroups[node.parent?.value]) {
                    xorGroups[node.parent?.value] = [];
                }
                // xorGroups[node.parent.value].push(node.value);
                if (node.children) {
                    node.children.forEach(child => {
                        xorGroups[node.parent.value].push(child.value);
                    });
                }
            }
            if (node.groupType === "and") {
                if (!andGroups[node.parent?.value]) {
                    andGroups[node.parent?.value] = [];
                }
                // andGroups[node.parent.value].push(node.value);
                if (node.children) {
                    node.children.forEach(child => {
                        andGroups[node.parent.value].push(child.value);
                    });
                }
            }

            // Recursively process children
            if (node.children) {
                node.children.forEach(traverseTree);
            }
        };

        // Start processing from the root node
        if (treeData[0]) traverseTree(treeData[0]);

        // Selected Nodes
        const selectedNodes = {
            or: {},
            xor: {},
            and: {},
            mandatory: {},
        };

        // checked.forEach((value) => {
        //     const node = findFeatureByValue(value, treeData[0]);
        //     if (node?.parent?.groupType === "or") {
        //         if (!selectedNodes.or[node.parent.value]) {
        //             selectedNodes.or[node.parent.value] = [];
        //         }
        //         selectedNodes.or[node.parent.value].push(node.value);
        //     } else if (node?.parent?.groupType === "xor") {
        //         if (!selectedNodes.xor[node.parent.value]) {
        //             selectedNodes.xor[node.parent.value] = [];
        //         }
        //         selectedNodes.xor[node.parent.value].push(node.value);
        //     } else if (node?.parent?.groupType === "and") {
        //         if (!selectedNodes.and[node.parent.value]) {
        //             selectedNodes.and[node.parent.value] = [];
        //         }
        //         selectedNodes.and[node.parent.value].push(node.value);
        //     }
        // });

        let mandatoryCount = 0;
        checked.forEach((value) => {
            const node = findFeatureByValue(value, treeData[0]);
            // selectedNodes.mandatory[node.value] = [];
            // selectedNodes.mandatory =  [];
            if (node?.parent?.groupType === "or") {
                if (!selectedNodes.or[node.parent.parent.value]) {
                    selectedNodes.or[node.parent.parent.value] = [];
                }
                selectedNodes.or[node.parent.parent.value].push(node.value);
            } else if (node?.parent?.groupType === "xor") {
                if (!selectedNodes.xor[node.parent.parent.value]) {
                    selectedNodes.xor[node.parent.parent.value] = [];
                }
                selectedNodes.xor[node.parent.parent.value].push(node.value);
            } else if (node?.parent?.groupType === "and") {
                if (!selectedNodes.and[node.parent.parent.value]) {
                    selectedNodes.and[node.parent.parent.value] = [];
                }
                selectedNodes.and[node.parent.parent.value].push(node.value);
            }
            if (node.mandatory) {
                selectedNodes.mandatory[mandatoryCount] = node.value;
                mandatoryCount++;
            }
        });

        //manually add treedata into payload.tree to avoid circular structure error

        return {
            tree: treeData,
            mandatory: mandatoryNodes,
            or: orGroups,
            xor: xorGroups,
            and: andGroups,
            selected: selectedNodes,
        };
    };


    const handleCheck = (value, isChecked) => {
        const rootNode = treeData[0];
        let updatedChecked = [...checked];

        const updateNodeSelection = (node, isSelecting) => {
            // Special handling for root node
            if (node.value === rootNode.value && !isSelecting) {
                updatedChecked = [];
                return;
            }

            if (isSelecting) {
                if (node.mandatory) {
                    updatedChecked = findMandatoryNodes(rootNode);
                    updatedChecked.push(node.value);
                    updatedChecked.push(node.parent.value);
                    if (!updatedChecked.includes(rootNode.value)) {
                        updatedChecked.push(rootNode.value);
                    }
                    return;
                }
            }

            if (!isSelecting) {
                //check if node is mandatory
                if (node.mandatory) {
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
            if (checkXOR) {
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
            }

            // Add or remove the current node
            if (isSelecting) {
                if (!updatedChecked.includes(node.value)) {
                    // updatedChecked.push(node.value);
                    //recurively check all parent nodes
                    let currentNode = node;
                    while (currentNode !== rootNode) {
                        if (!updatedChecked.includes(currentNode.value)) {
                            updatedChecked.push(currentNode.value);
                        }
                        currentNode = currentNode.parent;
                    }
                    updatedChecked.push(rootNode.value);
                    //push all mandatory nodes if not already selected
                    const mandatoryNodes = findMandatoryNodes(rootNode);
                    mandatoryNodes.forEach(mandatoryNode => {
                        if (!updatedChecked.includes(mandatoryNode)) {
                            updatedChecked.push(mandatoryNode);
                        }
                    });
                }

                //select parent nodes
                if (node.parent) {
                    if (!updatedChecked.includes(node.parent.value)) {
                        updatedChecked.push(node.parent.value);
                    }
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
                    if (node.parent.mandatory) {
                        updatedChecked = []
                    }
                    //recursively deselect all parent nodes if other children are not selected
                    let currentNode = node.parent;
                    while (currentNode !== rootNode) {
                        const allSiblingsDeselected = currentNode.children.every(
                            child => !updatedChecked.includes(child.value)
                        );
                        if (allSiblingsDeselected) {
                            updatedChecked = updatedChecked.filter(v => v !== currentNode.value);
                        }
                        currentNode = currentNode.parent;
                        if (currentNode.mandatory) {
                            updatedChecked = []
                        }
                    }

                }
            }
            // //make a check for mandatory nodes, if one is deselected, deselect all nodes
            // const mandatoryNodes = findMandatoryNodes(rootNode);
            // const mandatoryNodesSelected = mandatoryNodes.every(node => updatedChecked.includes(node));
            // if (!mandatoryNodesSelected) {
            //     updatedChecked = []
            // }
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

    const handleExpand = (value) => {
        setExpanded((prev) =>
            prev.includes(value)
                ? prev.filter((v) => v !== value)
                : [...prev, value]
        );
    };

    const renderNode = (node) => {
        return (
            <div key={node.value}>
                <Node mandatory={node.mandatory ? "true" : "false"}>
                    {/* Folder Expand Icon */}
                    {node.children && node.children.length > 0 && (
                        <ExpandIconWrapper onClick={() => handleExpand(node.value)}>
                            {expanded.includes(node.value) ? (
                                <FontAwesomeIcon icon={faChevronDown} />
                            ) : (
                                <FontAwesomeIcon icon={faChevronRight} />
                            )}
                        </ExpandIconWrapper>
                    )}

                    {/* Checkbox, Folder Icon, and Name in Same Line */}
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            width: "100%",
                        }}
                        onClick={() =>
                            handleCheck(node.value, !checked.includes(node.value))
                        }
                    >
                        {/* Checkbox */}
                        <div style={{ marginRight: "10px" }}>
                            {checked.includes(node.value) ? (
                                <FontAwesomeIcon icon={faCheckSquare} />
                            ) : (
                                <FontAwesomeIcon icon={faSquare} />
                            )}
                        </div>

                        {/* Folder Icon */}
                        <FolderIconWrapper>
                            <FontAwesomeIcon
                                icon={
                                    node.mandatory ? faFolderOpen : faFolder
                                }
                                style={{
                                    color: node.mandatory ? "red" : "#34495e",
                                }}
                            />
                        </FolderIconWrapper>

                        {/* Node Label */}
                        <NodeLabel mandatory={node.mandatory ? "true" : "false"}>
                            {node.label}
                        </NodeLabel>
                    </div>
                </Node>

                {/* Render Child Nodes */}
                {node.children && expanded.includes(node.value) && (
                    <div style={{ paddingLeft: "20px" }}>
                        {node.children.map((child) => renderNode(child))}
                    </div>
                )}
            </div>
        );
    };



    return (
        <Container>
            <Title>Feature Model</Title>
            <FileUploadWrapper>
                <input type="file" accept=".xml" onChange={handleFileUpload} />
                {error && <ErrorMessage>{error}</ErrorMessage>}
            </FileUploadWrapper>

            {/* add a checkbox here to toggle check xor */}
            Click here to check for XOR groups <input type="checkbox" id="checkXOR" name="checkXOR" value={checkXOR} onChange={() => setCheckXOR(!checkXOR)} />
            <br />
            <br />

            <TreeWrapper>
                {treeData.length === 0 ? (
                    <div>Loading...</div>
                ) : (
                    treeData.map((rootNode) => renderNode(rootNode))
                )}
            </TreeWrapper>
            <br />
            <button onClick={validateSelection}>Validate Selection</button>
            <br />
            <br />
            <input type="text" placeholder="Enter English" onChange={(e) => setEnglish(e.target.value)} /> 
            <button onClick={translate}>Translate</button>
            <br />
            {propositionalLogic ? (
                <div>
                    <h1>Propositional Logic</h1>
                    <p>{propositionalLogic}</p>
                </div>
            ) : (
                "no translation available"
            )}
        </Container>
    );
};

export default FeatureTree;
