
import React from "react";
import Button from "./DropdownButton";
import DropdownCard from "./DropdownCard";

const DropdownParent = ({data, addFilterEntry, filterEntries}) => {
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
            <Button onClick={() => setOpen(open => !open)}/>
            {open && <DropdownCard data={data} setOpen={setOpen} addFilterEntry={addFilterEntry} filterEntries={filterEntries}/>}
        </div>
    )
}

export default DropdownParent;