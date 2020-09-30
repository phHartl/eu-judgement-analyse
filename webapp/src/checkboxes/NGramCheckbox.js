// import React from 'react';
//
// class NGramCheckbox extends React.Component {
//     constructor() {
//         super();
//
//         this.state = {
//             checked: false,
//             n: "",
//             nLimit: ""
//         };
//         this.handleChange = this.handleChange.bind(this);
//     }
//
//     handleChange() {
//         this.setState({
//             checked: !this.state.checked
//         })
//     }
//
//     handleInputChange(event) {
//         const target = event.target;
//         const value = target.type === 'checkbox' ? target.checked : target.value;
//         const name = target.name;
//         this.setState({
//             [name]: value
//         });
//     }
//
//     render() {
//         const hidden = this.state.checked ? '' : 'hidden';
//
//         return (
//             <div>
//                 <div className="row">
//                     <label htmlFor="ngrams" className="checkboxes">N-Grams<input type="checkbox" name="ngrams"
//                                                                                  id="ngrams"
//                                                                                  className="checkboxes"
//                                                                                  checked={this.state.checked}
//                                                                                  onChange={this.handleChange}/></label>
//                 </div>
//
//                 <div className={"row"} style={{visibility: hidden}}>
//                     <div className="col-25">
//                         <label htmlFor="n">N: </label>
//                     </div>
//                     <div className="col-75">
//                         <input type="text" name="n" id="n" className="input-large"
//                                onChange={this.handleInputChange}/>
//                     </div>
//                 </div>
//
//                 <div className={"row"} style={{visibility: hidden}}>
//                     <div className="col-25">
//                         <label htmlFor="n-limit">Limit: </label>
//                     </div>
//                     <div className="col-75">
//                         <input type="text" name="nLimit" id="n-limit" className="input-large"
//                                onChange={this.handleInputChange()}/>
//                     </div>
//                 </div>
//
//
//
//             </div>
//         )
//     }
// }
//
// export default NGramCheckbox;