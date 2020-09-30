import React from 'react';
import {
    BAR_CHART, CASE_AFFECTING_API_DESC, DECISIONS_ON_COST_API_DESC,
    DOWNLOAD, END_DATE_API_DESC,
    MOST_FREQUENT_WORD_VISUALIZATION,
    N_GRAM_VISUALIZATION, START_DATE_API_DESC,
    TOKEN_VISUALIZATION,
    WORDCLOUD
} from "./Constants";


let requestJSON = "";

class SearchForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            language: "english",
            nGramsChecked: false,
            nLimit: "",
            n: "",
            readabilityChecked: false,
            tokensChecked: false,
            tokenLimit: "",
            tokenCountChecked: false,
            tokenRemoveStopWords: false,
            tokenRemovePunctuation: false,
            wordCountChecked: false,
            wordCountRemoveStopWords: false,
            mostFrequentWordsChecked: false,
            mostFrequentWordsLimit: "",
            mostFrequentWordsRemoveStopWords: false,
            mostFrequentWordsLemmatise: false,
            sentencesChecked: false,
            sentenceCountChecked: false,
            elementsToSearchFor: [],
            startDate : "",
            endDate: "",
        };

        this.handleInputChange = this.handleInputChange.bind(this);
        this.searchInputChange = this.searchInputChange.bind(this);
        this.handleVisualizationChange = this.handleVisualizationChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    searchInputChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
        this.modifySearchArray(name, value);

        this.handleInputChange(event);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
        console.debug(this.state);
    }

    modifySearchArray(name, value) {
        // add element to search array on new input
        if (!this.state.elementsToSearchFor.includes(name) && value !== "") {
            // this.setState((state) => {
            //     let array = state.elementsToSearchFor;
            //     array.push(name);
            //     // array = array.slice(1);
            //     return {elementsToSearchFor: array};
            // });
            let array = this.state.elementsToSearchFor;
            array.push(name);
            this.state.elementsToSearchFor = array;
        }

        // remove element from search array if the input is deleted
        if (this.state.elementsToSearchFor.includes(name) && value === "") {
            this.setState((state) => {
                let array = state.elementsToSearchFor;
                for (var i = array.length - 1; i >= 0; i--) {
                    if (array[i] === name) {
                        array.splice(i, 1);
                    }
                }
                return {elementsToSearchFor: array};
            });
        }
        console.debug(this.state.elementsToSearchFor);
    }

    handleVisualizationChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
        console.debug("visulaization change: " + name + ": " + value);
        this.props.onVisualizationSelected(name, value);
    }

    handleSubmit(event) {
        let alertString = "";
        for (let state in this.state) {
            alertString += this.state[state];
            alertString += "\n";
        }
        // alert('A search was submitted: \n' + alertString);
        event.preventDefault();
        this.requestJSON();
    }


    requestJSON() {
        let json = {};

        json.language = this.getSelectedLanguage();
        json.corpus = this.getSearchInputValues();
        json.analysis = this.addAnalysisOptionsToJson();
        this.props.onResponse(json);
        console.debug(json);
    }


    addAnalysisOptionsToJson() {
        let analysisTypes = [];
        if (this.state.n === "") {
            this.state.n = 2;
        }
        if (this.state.nGramsChecked) {
            analysisTypes.push({
                type: "n-grams",
                n: parseInt(this.state.n),
                limit: parseInt(this.state.nLimit)
            })
        }

        if (this.state.readabilityChecked) {
            analysisTypes.push({
                type: "readability"
            })
        }

        if (this.state.tokensChecked) {
            analysisTypes.push({
                type: "tokens",
                "remove stop words": this.state.tokenRemoveStopWords,
                "remove punctuation": this.state.tokenRemovePunctuation,
                limit: parseInt(this.state.tokenLimit)
            })
        }

        if (this.state.mostFrequentWordsChecked) {
            analysisTypes.push({
                type: "most frequent words",
                "remove stop words": this.state.mostFrequentWordsRemoveStopWords,
                lemmatise: this.state.mostFrequentWordsLemmatise,
                limit: parseInt(this.state.mostFrequentWordsLimit)
            })
        }

        if (this.state.sentenceCountChecked) {
            analysisTypes.push({
                type: "sentence count"
            })
        }

        if (this.state.tokenCountChecked) {
            analysisTypes.push({
                type: "token count"
            })
        }

        if (this.state.wordCountChecked) {
            analysisTypes.push({
                type: "word count",
                "remove stop words": this.state.wordCountRemoveStopWords
            })
        }


        return analysisTypes;
    }

    getSelectedLanguage() {
        return this.state.language === "english" ? "en" : "de";
    }


    getSearchInputValues() {
        let elementsToSearchFor = this.state.elementsToSearchFor;
        let corpus = [];
        let date = this.getDateForSearch();

        for (let element of elementsToSearchFor) {
            // date needs to be formatted separately
            if (element === "startDate" || element === "endDate") {
                continue;
            }
            element = this.getDatabaseKeyForElement(element);
            let entry = {
                column: element,
                value: this.state[element]
            };
            corpus.push(entry);
        }
        if (date !== null) {
            corpus.push(date);
        }
        console.debug(corpus);
        return corpus;
    }

    getDateForSearch() {
        let startDate, endDate;
        if (this.state.startDate !== "" && this.state.endDate !== "") {
            startDate = this.state.startDate;
            endDate = this.state.endDate;
        } else {
            return null;
        }


        return {
            column: "date",
            "start date": startDate,
            "end date": endDate
        };
    }

    getDatabaseKeyForElement(element) {
        switch (element) {
            case "startDate":
                return START_DATE_API_DESC;

            case "endDate":
                return END_DATE_API_DESC;

            case "caseAffecting":
                return CASE_AFFECTING_API_DESC;

            case "decisionsOnCost":
                return DECISIONS_ON_COST_API_DESC;

            default:
                return element;
        }
    }


    render() {

        const nGramsHidden = this.state.nGramsChecked ? '' : 'none';
        const tokensHidden = this.state.tokensChecked ? '' : 'none';

        return (
            <form className="feature-container" onSubmit={this.handleSubmit}>
                <div className="row">
                    <div className="col-25">
                        <label htmlFor="quickSearch" className="search-label">Quick Search</label>
                    </div>
                    <div className="col-75">
                        <input type="text" name="quickSearch" id="quickSearch" className="input-large"
                               onChange={this.searchInputChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="language" className="search-label">Language</label>
                    </div>
                    <div className="col-25">
                        <select name="language" id="language" className="input-large" onChange={this.searchInputChange}>
                            <option value="english">English</option>
                            <option value="german">German</option>
                        </select>
                    </div>

                    <div className="col-25">
                        <label htmlFor="parties" className="search-label">Parties</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="parties" id="parties" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="startDate" className="search-label">Start Date</label>
                    </div>
                    <div className="col-25">
                        <input type="date" name="startDate" id="startDate" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="endDate" className="search-label">End Date</label>
                    </div>
                    <div className="col-25">
                        <input type="date" name="endDate" id="endDate" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="author" className="search-label">Author</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="author" id="author" className="input-large"
                               onChange={this.searchInputChange}/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="judge" className="search-label">Judge</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="judge" id="judge" className="input-large"
                               onChange={this.searchInputChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="celex" className="search-label">Celex</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="celex" id="celex" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="title" className="search-label">Title</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="title" id="title" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="subject" className="search-label">Subject</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="subject" id="subject" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="endorsements" className="search-label">Endorsements</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="endorsements" id="endorsements" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="grounds" className="search-label">Grounds</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="grounds" id="grounds" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="decisionsOnCost" className="search-label">Decisions on Cost</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="decisionsOnCost" id="decisionsOnCost" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="operativePart" className="search-label">Operative Part</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="operativePart" id="operativePart" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    <div className="col-25">
                        <label htmlFor="ecli" className="search-label">ECLI</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="ecli" id="ecli" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="keywords" className="search-label">Keywords</label>
                    </div>
                    <div className="col-25">
                        <input type="text" name="keywords" id="keywords" className="input-large"
                               onChange={this.searchInputChange}/><br/>
                    </div>

                    // new elements here


                </div>


                <div className="row" style={{paddingTop: "30px"}}>
                    Analysis
                </div>


                {/* Begin N-Grams Checkbox + Dropdown*/}
                <div className="row">
                    <div className="col-50">
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name="nGramsChecked"
                                   id="ngrams"
                                   className="checkboxes"
                                   checked={this.state.nGramsChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="ngrams" className="checkboxes">N-Grams</label>
                        </div>

                        <div className={"row"} style={{display: nGramsHidden}}>
                            <div className="col-50">
                                <label htmlFor="n-limit">Limit: </label>
                            </div>
                            <div className="col-50">
                                <input type="number" name="nLimit" id="n-limit" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>

                        <div className={"row"} style={{display: nGramsHidden}}>
                            <div className="col-50">
                                <label htmlFor={N_GRAM_VISUALIZATION}>Visualization: </label>
                            </div>
                            <div className="col-50">
                                <select className="input-large" name={N_GRAM_VISUALIZATION} id={N_GRAM_VISUALIZATION} onChange={this.handleVisualizationChange}>
                                    <option value={BAR_CHART}>Bar Chart</option>
                                    <option value={WORDCLOUD}>Wordcloud</option>
                                    <option value={DOWNLOAD}>Download</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    {/*End N-Grams Dropdown*/}

                    {/*Readability*/}
                    <div className="col-50 ks-cboxtags">
                        <input type="checkbox"
                               name="readabilityChecked"
                               id="readability"
                               className="checkboxes"
                               onChange={this.handleInputChange}/>
                        <label htmlFor="readability" className="checkboxes">Readability</label>
                    </div>
                    {/*End Readability*/}
                </div>
                <div className="row">
                    {/*Begin Tokens Checkbox + Dropdown*/}
                    <div className="col-50">
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name="tokensChecked"
                                   id="tokens"
                                   className="checkboxes"
                                   checked={this.state.tokensChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="tokens" className="checkboxes">Tokens</label>
                        </div>

                        {/*Token settings*/}
                        <div className={"row"} style={{display: tokensHidden}}>
                            <div className="col-50">
                                <label htmlFor={"tokenRemoveStopWords"}>Remove Stop Words: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="tokenRemoveStopWords" id="tokenRemoveStopWords" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>
                        <div className={"row"} style={{display: tokensHidden}}>
                            <div className="col-50">
                                <label htmlFor={"tokenRemovePunctuation"}>Remove Punctuation: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="tokenRemovePunctuation" id="tokenRemovePunctuation" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>
                        <div className={"row"} style={{display: tokensHidden}}>
                            <div className="col-50">
                                <label htmlFor="token-limit">Limit: </label>
                            </div>
                            <div className="col-50">
                                <input type="number" name="tokenLimit" id="token-limit" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>
                        <div className={"row"} style={{display: tokensHidden}}>
                            <div className="col-50">
                                <label htmlFor={TOKEN_VISUALIZATION}>Visualization: </label>
                            </div>
                            <div className="col-50">
                                <select className="input-large" name={TOKEN_VISUALIZATION} id={TOKEN_VISUALIZATION} onChange={this.handleVisualizationChange}>
                                    <option value={WORDCLOUD}>Wordcloud</option>
                                    <option value={BAR_CHART}>Bar Chart</option>
                                    <option value={DOWNLOAD}>Download</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    {/*End Tokens Dropdown*/}

                    {/*Begin Token Count*/}
                    <div className="col-50">
                        <div className="row ks-cboxtags">
                                <input type="checkbox"
                                       name={"tokenCountChecked"}
                                       id={"tokenCount"}
                                       className={"checkboxes"}
                                       checked={this.state.tokenCountChecked}
                                       onChange={this.handleInputChange}/>
                            <label htmlFor="tokenCount" className="checkboxes">
                                Token Count</label>
                        </div>
                    </div>
                    {/* End Token Count */}
                </div>

                <div className={"row"}>
                    {/*Begin Word Count */}
                    <div className={"col-50"}>
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name={"wordCountChecked"}
                                   id={"wordCountChecked"}
                                   className={"checkboxes"}
                                   checked={this.state.wordCountChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="wordCountChecked" className="checkboxes">Word Count</label>
                        </div>

                        <div className={"row"} style={{display: this.state.wordCountChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="wordCountRemoveStopWords">Remove stop words: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="wordCountRemoveStopWords" id="wordCountRemoveStopWords" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>
                    </div>
                    {/* End Word Count */}

                    {/*Begin most frequent words */}
                    <div className={"col-50"}>
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name={"mostFrequentWordsChecked"}
                                   id={"mostFrequentWords"}
                                   className={"checkboxes"}
                                   checked={this.state.mostFrequentWordsChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="mostFrequentWords" className="checkboxes">Most Frequent Words</label>
                        </div>

                        <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="mostFrequentWordsRemoveStopWords">Remove stop words: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="mostFrequentWordsRemoveStopWords" id="mostFrequentWordsRemoveStopWords" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>

                        <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="mostFrequentWordsLemmatise">Lemmatise: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="mostFrequentWordsLemmatise" id="mostFrequentWordsLemmatise" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>

                        <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="mostFrequentWordsLimit">Limit: </label>
                            </div>
                            <div className="col-50">
                                <input type="number" name="mostFrequentWordsLimit" id="mostFrequentWordsLimit" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>

                            <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                                <div className="col-50">
                                    <label htmlFor={MOST_FREQUENT_WORD_VISUALIZATION}>Visualization: </label>
                                </div>
                                <div className="col-50">
                                    <select className="input-large" name={MOST_FREQUENT_WORD_VISUALIZATION} id={MOST_FREQUENT_WORD_VISUALIZATION} onChange={this.handleVisualizationChange}>
                                        <option value={BAR_CHART}>Bar Chart</option>
                                        <option value={WORDCLOUD}>Wordcloud</option>
                                        <option value={DOWNLOAD}>Download</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* End most frequent words */}
                </div>
                <div className="row">
                    {/* Begin sentences}*/}
                    <div className="col-50">
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name={"sentencesChecked"}
                                   id={"sentencesChecked"}
                                   className={"checkboxes"}
                                   checked={this.state.sentencesChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="sentencesChecked" className="checkboxes">Sentences</label>
                        </div>
                    </div>
                    {/* End Sentences */}

                    {/* Begin sentence count */}
                    <div className="col-50">
                        <div className="row ks-cboxtags">
                            <input type="checkbox"
                                   name={"sentenceCountChecked"}
                                   id={"sentenceCountChecked"}
                                   className={"checkboxes"}
                                   checked={this.state.sentenceCountChecked}
                                   onChange={this.handleInputChange}/>
                            <label htmlFor="sentenceCountChecked" className="checkboxes">Sentence Count</label>
                        </div>
                    </div>


                </div>

                <input type="submit" name="submitSearch" id="submitSearch" className="generic-button"/>

            </form>
        );
    }
}


export default SearchForm;