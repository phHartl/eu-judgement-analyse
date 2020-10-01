
import React from "react";
import {START_DATE_API_DESC} from "./Constants";

const FilterEntry = ({elements, index, text, onChange}) => {
    const [isNegated, setNegated] = React.useState(false);
    console.debug(elements[index]);
    console.debug(elements[index][Object.keys(elements[index])[0]].inputType);
    let inputType = elements[index][Object.keys(elements[index])[0]].inputType;
    let name = elements[index][Object.keys(elements[index])[0]].key;

    if (name === "date") {
        return (
            <div>
                <div className="row">
                    <div className="col-25">
                        <label htmlFor="startDate" className="search-label">Start Date</label>
                    </div>

                    <div className="col-75">
                        <input type={inputType} className="input-large" name="startDate" onChange={onChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="endDate" className="search-label">End Date</label>
                    </div>

                    <div className="col-75">
                        <input type={inputType} className="input-large" name="endDate" onChange={onChange}/>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="row">
            <div className="col-25">
                <label htmlFor={name} className="search-label">{text}</label>
            </div>

            <div className="col-75">
                <input type={inputType} className="input-large" name={name} onChange={onChange}/>
            </div>
        </div>
    )
}

export default FilterEntry;