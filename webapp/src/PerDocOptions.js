
import React from "react";

const PerDocOptions = ({ data, onOptionSelected, id, celexNumbers }) => {

    if (data === undefined || data === null) {
        return null;
    }

    return (
        data.map((item, i) => (
            <option id={id + "-" + i} value={item} key={i} onClick={() => onOptionSelected(i)}>{celexNumbers[i]}</option>
        ))
    )
}

export default PerDocOptions;
