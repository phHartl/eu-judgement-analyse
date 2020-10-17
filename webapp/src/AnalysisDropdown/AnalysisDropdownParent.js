
import React from "react";
import AnalysisDropdownButton from "./AnalysisDropdownButton";
import AnalysisDropdownCard from "./AnalysisDropdownCard";

function removeAlreadyAddedElements(data, alreadyAdded) {

    if (typeof alreadyAdded === "undefined") {
        return data;
    }
    for (const element of Object.keys(data[0])) {
        for (const addedElement of alreadyAdded) {
            if (typeof data[0][element] === "undefined") {
                continue;
            }
            if (addedElement.description === data[0][element].description) {
                delete data[0][element];
            }
        }
    }
    return data;
}

const AnalysisDropdownParent = ({data, alreadyAdded, addAnalysisOption}) => {
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
            <AnalysisDropdownButton onClick={() => setOpen(open => !open)}/>
            {open && <AnalysisDropdownCard data={backupData} setOpen={setOpen} addAnalysisMethod={addAnalysisOption}/>}
        </div>
    )
}

export default AnalysisDropdownParent;