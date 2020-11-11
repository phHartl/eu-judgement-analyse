import React from "react";

function getAnalysisOptionsArray(data) {
    let array = [];
    for (const element in data[0]) {
        array.push(data[0][element]);
    }
    return array;
}


const AnalysisDropdownCard = ({data = [], setOpen, addAnalysisMethod}) => {

    if (data === null) {
        return null;
    }

    data = getAnalysisOptionsArray(data);

    return (
        <div className="dropdown-item-container">
            {data.map((item, i) => (
                <button className="dropdown-item" key={i} onClick={() => {
                    setOpen(false);
                    addAnalysisMethod(item);
                }}>
                    {item.description}
                </button>
            ))}
        </div>
    )
}

export default AnalysisDropdownCard;