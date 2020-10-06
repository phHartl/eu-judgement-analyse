import React from "react";


const FilterEntryParent = ({data = [], getNegationIconClass, onChange, onDelete, onSetOperator}) => {


    return (
        data.map((item, i) => (
            <div className="row" key={i}>
                <div className="col-25">
                    <label htmlFor={item.key}
                           className="search-label">{item.text}</label>
                </div>

                <div className="col-65">
                    <input type={item.inputType} className="input-large"
                           name={item.key} onChange={onChange}/>
                </div>

                <div className="col-5">
                    <a className="remove-filter-entry" onClick={() => onDelete(item)}>
                        <i className="fas fa-trash"/>
                    </a>
                </div>

                <div className="col-2">
                    <a className={"set-operator-entry"}  onClick={() => onSetOperator(item)}>
                        <i className={getNegationIconClass(item)} />
                    </a>
                </div>
            </div>
        ))
    )
}

export default FilterEntryParent;