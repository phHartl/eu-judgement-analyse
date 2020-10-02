import React from "react";

let filterNames;
let dataBackup;
let filterData;
const DropdownCard = ({data = [], setOpen, addFilterEntry, filterEntries}) => (
    <div className="dropdown-item-container">
        {fillFilterNames(data)}
        {filterData.map((item, i) => (
                    <button className="dropdown-item" key={i} onClick={() => {
                        setOpen(false);
                        addFilterEntry(i, item, dataBackup, filterEntries);
                    }}>
                        {item}
                    </button>
        ))}
    </div>
);

function fillFilterNames(filterElements) {
    let returnArray = [];
    dataBackup = filterElements;
    for (let element of filterElements) {
        returnArray.push(element[Object.keys(element)[0]].text)
    }
    filterData = returnArray;
}

export default DropdownCard;