import React from "react";
import AnalysisOptions from "./AnalysisOptions";
import VisualizationOptions from "./VisualizationOptions";


const AnalysisOptionsParent = ({data, state, handleInputChange, handleVisualizationChange}) => {


    return (
        data.map((item, i) => (
            <div key={i} className="col-50">
                <div className="row ks-cboxtags">
                    <input type="checkbox"
                           name={item.name}
                           id={item.id}
                           className={"checkboxes fancy-checkbox"}
                           onChange={handleInputChange}
                    />
                    <label htmlFor={item.id} className={"checkboxes fancy-label"}
                           style={{width: "65%"}}>{item.description}

                        <div className="analysis-options row">
                                <div className="row inner-option" style={{display: state[item.name] ? "" : "none"}}>
                                    <AnalysisOptions options={item.options} handleInputChange={handleInputChange}/>
                                </div>

                                <div className="row" style={{display: state[item.name] ? "" : "none"}}>
                                    <div key={i} className="row"
                                         style={{display: item.visualizationOptions === null ? "none" : ""}}>
                                        <div className="col-50 inner-option">
                                            <label htmlFor={item.name + "Visualization"}>Visualization</label>
                                        </div>

                                        <div className="col-50 inner-input">
                                            <select className="input-large" name={item.name + "Visualization"}
                                                    id={item.name + "Visualization"}
                                                    onChange={handleVisualizationChange}>
                                                <VisualizationOptions name={item.name}
                                                                      visualizationOptions={item.visualizationOptions}/>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                        </div>
                    </label>


                </div>


            </div>
        ))
    )
}

export default AnalysisOptionsParent;