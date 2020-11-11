import React from "react";


const NamedEntityListEntry = ({data = []}) => {

    if (data === null) {
        return null;
    }

    return (
        <div className="named-entity-list-item">
            {data.map((item, i) => (
                <li key={i}>
                    {item}
                </li>
            ))}
        </div>
    )
}

export default NamedEntityListEntry;
