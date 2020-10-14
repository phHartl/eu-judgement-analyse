import React from 'react';

class SearchForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            quickSearch: "",
            language: "english",
            author: "",
            judge: "",
            participants: "",
            from: "",
            to: ""
        };
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
    }

    handleSubmit(event) {
        let alertString = "";
        for (let state in this.state) {
            alertString += this.state[state];
            alertString += "\n";
        }
        alert('A search was submitted: \n' + alertString);
        event.preventDefault();
    }

    render() {
        return (
            <form className="feature-container" onSubmit={this.handleSubmit}>
                <div className="row">
                    <div className="col-25">
                        <label htmlFor="quickSearch">Quick Search</label>
                    </div>
                    <div className="col-75">
                        <input type="text" name="quickSearch" id="quickSearch" className="input-large"
                               onChange={this.handleInputChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="language">Language</label>
                    </div>
                    <div className="col-75">
                        <select name="language" id="language" className="input-large" onChange={this.handleInputChange}>
                            <option value="english">English</option>
                            <option value="german">German</option>
                            <option value="both">Both</option>
                        </select>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="author">Author</label>
                    </div>
                    <div className="col-75">
                        <input type="text" name="author" id="author" className="input-large"
                               onChange={this.handleInputChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="judge">Judge</label>
                    </div>
                    <div className="col-75">
                        <input type="text" name="judge" id="judge" className="input-large"
                               onChange={this.handleInputChange}/>
                    </div>
                </div>


                <div className="row">
                    <div className="col-25">
                        <label htmlFor="participants">Participants</label>
                    </div>
                    <div className="col-75">
                        <input type="text" name="participants" id="participants" className="input-large"
                               onChange={this.handleInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="from">From</label>
                    </div>
                    <div className="col-75">
                        <input type="number" name="from" id="from" className="input-large"
                               onChange={this.handleInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="to">To</label>
                    </div>
                    <div className="col-75">
                        <input type="number" name="to" id="to" className="input-large"
                               onChange={this.handleInputChange}/><br/>
                    </div>
                </div>
                <input type="submit" name="submitSearch" id="submitSearch" className="generic-button"/>

            </form>
        );
    }
}


export default SearchForm;