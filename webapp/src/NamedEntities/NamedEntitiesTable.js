import React from "react";
import NamedEntityListEntry from "./NamedEntityListEntry";


const NamedEntitiesTable = ({data = []}) => {

    if (data === null) {
        return null;
    }

    let columnSize = parseInt((100 / data.length).toString());

    return (
        <div>
        <span className="named-entity-container row">
            {data.map((item, i) => (
                <div key={i} className={"col-" + columnSize}>
                    <h5>{item[0]}</h5>
                    <ul>
                        <NamedEntityListEntry data={item[1]}/>
                    </ul>
                </div>
            ))}
        </span>
        </div>
    )
}

export default NamedEntitiesTable;
