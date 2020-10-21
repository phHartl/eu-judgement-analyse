
import React from "react";
import FilterDropdownButton from "./FilterDropdownButton";
import FilterDropdownCard from "./FilterDropdownCard";

function removeAlreadyAddedElements(data, alreadyAdded) {

    if (typeof alreadyAdded === "undefined") {
        return data;
    }

    for (let i = 0; i < data.length; i++) {
        for (const addedElement of alreadyAdded) {
            if (typeof data[i] === "undefined") {
                continue;
            }
            if (addedElement.key === data[i][Object.keys(data[i])[0]].key) {
                delete data[i];
            }
        }
    }

    return data;
}

const FilterDropdownParent = ({data, addFilterEntry, alreadyAdded, filterEntries}) => {
    const [open, setOpen] = React.useState(false);
    const drop = React.useRef(null);

    function handleClick(e) {
        if (!e.target.closest(`.${drop.current.className}`) && open) {
            setOpen(false);
        }
    }

    React.useEffect(() => {
        document.addEventListener("click", handleClick);
        return () => {
            document.removeEventListener("click", handleClick)
        }
    })

    let backupData = JSON.parse(JSON.stringify(data))
    backupData = removeAlreadyAddedElements(backupData, alreadyAdded);

    return (
        <div className="dropdown" ref={drop}>
            <FilterDropdownButton onClick={() => setOpen(open => !open)}/>
            {open && <FilterDropdownCard data={backupData} setOpen={setOpen} addFilterEntry={addFilterEntry} filterEntries={filterEntries}/>}
        </div>
    )
}

export default FilterDropdownParent;