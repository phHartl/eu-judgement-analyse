import React from "react";
import PerDocOptions from "./PerDocOptions";


function updateValue() {
    let selector = document.getElementById("readabilityPerDocSelector");
    if (selector === null) {
        return "";
    }

    return selector.value;
}

const PerDocSelector = ({data, onChange, onOptionSelected, id, celexNumbers}) => {

    if (data === undefined || data === null) {
        return null;
    }

    return (
        <select id={"readabilityPerDocSelector"} onChange={onChange} className="per-document-selector">
            <PerDocOptions data={data} onOptionSelected={onOptionSelected} id={id} celexNumbers={celexNumbers}/>
        </select>
    )
};

export default PerDocSelector;
