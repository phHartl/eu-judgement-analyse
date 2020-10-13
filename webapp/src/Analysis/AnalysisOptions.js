
import React from "react";

function getAnalysisOptionsArray(data) {
    let array = [];
    for (const element in data[0]) {
        array.push(data[0][element]);
    }
    return array;
}

const AnalysisOptions = ({options = [], handleInputChange}) => {

    if (options === null) {
        return null;
    }

    options = getAnalysisOptionsArray(options);

    return (
        options.map((item, i) => (
            <div key={i} className="row">
                <div className="col-50 inner-option">
                    <label htmlFor={item.id} className="check">{item.description}</label>
                </div>

                <div className="col-50 inner-input">
                    <input type={item.inputType} name={item.name} id={item.id} className="input-large toggle" onChange={handleInputChange}/>
                </div>
            </div>
        ))
    )
}

export default AnalysisOptions;