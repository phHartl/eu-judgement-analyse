
import React from "react";

const DownloadDataButton = ({description, data, downloadData}) => (
    <button type="button" className="download-data-button generic-button" onClick={() => downloadData(data)}>
        Download {description}
    </button>
);

export default DownloadDataButton;