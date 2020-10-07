
import React from "react";

const Button = ({ onClick }) => (
    <button type="button" className="add-filter-button" onClick={onClick}>
        + Filter
    </button>
);

export default Button;
