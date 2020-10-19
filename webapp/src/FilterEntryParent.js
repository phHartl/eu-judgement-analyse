import React from "react";


const FilterEntryParent = ({data = [], getNegationIconClass, getSearchIdentifierClass, onChange, onDelete, onSetOperator, onSetSearchIdentifier}) => {


    return (
        data.map((item, i) => (
            <div className="row filter-entry" key={i}>
                <div className="col-25">
                    <label htmlFor={item.key}
                           className="search-label">{item.text}</label>
                </div>

                <div className="col-60">
                    <input type={item.inputType} className="input-large"
                           name={item.key} onChange={onChange}/>
                </div>

                <div className="col-5">
                    <button type="button" className="remove-filter-entry filter-option-button"
                            onClick={() => onDelete(item)}>
                        <i className="fas fa-trash"/>
                    </button>
                </div>

                <div className="col-5">
                    <button type="button" className="filter-option-button" onClick={() => onSetOperator(item)}>
                        <i className={getNegationIconClass(item)}/>
                    </button>

                    {/*<span className="inner-input">*/}
                    {/*<input type="checkbox" className="toggle negated-checkbox" onChange={() => onSetOperator(item)}/>*/}
                    {/*</span>*/}

                </div>
                <div className="col-5" style={{display: item.displaySearchIdentifier}}>
                    {/*<button type="button" className="filter-option-button" onClick={() => onSetSearchIdentifier(item)}>*/}
                    {/*    <i className={getSearchIdentifierClass(item)}/>*/}
                    {/*</button>*/}
                    <span className="inner-input">
                    <input type="checkbox" className="toggle search-identifier-checkbox" onChange={() => onSetSearchIdentifier(item)}/>
                    </span>
                </div>

            </div>
        ))
    )
}

export default FilterEntryParent;