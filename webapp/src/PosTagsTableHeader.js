
import React from "react";
import {UNIVERSAL_POS_TAGS, UNIVERSAL_POS_TAGS_HINTS} from "./Constants";

const PosTagsTableHeader = () => {

    return (
        UNIVERSAL_POS_TAGS.map((item, i) => (
            <th className="pos-tags-per-doc-header" title={UNIVERSAL_POS_TAGS_HINTS[i]} key={i}>{item}</th>
        ))
    )
}

export default PosTagsTableHeader;
