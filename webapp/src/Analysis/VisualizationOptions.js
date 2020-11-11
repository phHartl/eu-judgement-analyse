import React from "react";
import {BAR_CHART, DOWNLOAD, WORDCLOUD} from "../Constants";

function getDisplayTextForVisualization(item) {
    switch (item) {
        case WORDCLOUD:
            return "Wordcloud";

        case BAR_CHART:
            return "Bar Chart";

        case DOWNLOAD:
            return "Download";

        default:
            return "";
    }
}

const VisualizationOptions = ({visualizationOptions = [], handleInputChange}) => {

    if (visualizationOptions === null) {
        return null;
    }

    return (
        visualizationOptions.map((item, i) => (
            <option value={item} key={i}>{getDisplayTextForVisualization(item)}</option>

        ))
    )
}

export default VisualizationOptions;