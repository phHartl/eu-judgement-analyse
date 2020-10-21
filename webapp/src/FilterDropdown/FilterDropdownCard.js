import React from "react";

let dataBackup;
let filterData;
const FilterDropdownCard = ({data = [], setOpen, addFilterEntry, filterEntries}) => (
    <div className="dropdown-item-container">
        {/*{debugData(data)}*/}
        {data.map((item, i) => (
                    <button className="dropdown-item" key={i} onClick={() => {
                        setOpen(false);
                        addFilterEntry(item);
                    }}>
                        {item[Object.keys(item)[0]].text}
                    </button>
        ))}
    </div>
);

function debugData(data) {
    console.debug(data[0][Object.keys(data[0])[0]].text);
}

function fillFilterNames(filterElements) {
    let returnArray = [];
    dataBackup = filterElements;
    for (const element of filterElements) {
        if (typeof element === "undefined") {
            continue;
        }
        returnArray.push(element[Object.keys(element)[0]].text)
    }
    console.debug(returnArray);
    filterData = returnArray;
}

export default FilterDropdownCard;