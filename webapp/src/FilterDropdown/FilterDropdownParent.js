
import React from "react";
import FilterDropdownButton from "./FilterDropdownButton";
import FilterDropdownCard from "./FilterDropdownCard";

const FilterDropdownParent = ({data, addFilterEntry, filterEntries}) => {
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

    return (
        <div className="dropdown" ref={drop}>
            <FilterDropdownButton onClick={() => setOpen(open => !open)}/>
            {open && <FilterDropdownCard data={data} setOpen={setOpen} addFilterEntry={addFilterEntry} filterEntries={filterEntries}/>}
        </div>
    )
}

export default FilterDropdownParent;