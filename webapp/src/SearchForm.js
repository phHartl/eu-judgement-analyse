import React from 'react';
import {
    AUTHOR,
    AUTHOR_API_DESC,
    BAR_CHART,
    CASE_AFFECTING_API_DESC,
    CELEX,
    CELEX_API_DESC,
    DATE,
    DATE_API_DESC, DECISIONS_ON_COST,
    DECISIONS_ON_COST_API_DESC,
    DOWNLOAD, ECLI, ECLI_API_DESC,
    END_DATE_API_DESC, ENDORSEMENTS, ENDORSEMENTS_API_DESC, GROUNDS, GROUNDS_API_DESC, KEYWORDS, KEYWORDS_API_DESC,
    MOST_FREQUENT_WORD_VISUALIZATION,
    N_GRAM_VISUALIZATION, OPERATIVE_PART, OPERATIVE_PART_API_DESC,
    PARTIES,
    PARTIES_API_DESC,
    START_DATE_API_DESC,
    SUBJECT,
    SUBJECT_API_DESC,
    TITLE,
    TITLE_API_DESC,
    TOKEN_VISUALIZATION,
    WORDCLOUD
} from "./Constants";
import DropdownParent from "./DropdownComponents/DropdownParent";
import FilterEntry from "./FilterEntry";
import FilterEntryParent from "./FilterEntryParent";


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
            startDate: "",
            endDate: "",
            dropdownData: "",
            filterEntries: [],
            filterValues: [],
            searchFilterElements: [{
                parties: {
                    key: PARTIES_API_DESC,
                    text: PARTIES,
                    displayed: false,
                    inputType: "text"
                }},
                {
                date: {
                    key: DATE_API_DESC,
                    text: DATE,
                    displayed: false,
                    inputType: "date"
                }},
                {
                author: {
                    key: AUTHOR_API_DESC,
                    text: AUTHOR,
                    displayed: false,
                    inputType: "text"
                }},
                {
                subject: {
                    key: SUBJECT_API_DESC,
                    text: SUBJECT,
                    displayed: false,
                    inputType: "text"
                }},
                {
                celex: {
                    key: CELEX_API_DESC,
                    text: CELEX,
                    displayed: false,
                    inputType: "text"
                }},
                {
                title: {
                    key: TITLE_API_DESC,
                    text: TITLE,
                    displayed: false,
                    inputType: "text"
                }},
                {
                endorsements: {
                    key: ENDORSEMENTS_API_DESC,
                    text: ENDORSEMENTS,
                    displayed: false,
                    inputType: "text"
                }},
                {
                grounds: {
                    key: GROUNDS_API_DESC,
                    text: GROUNDS,
                    displayed: false,
                    inputType: "text"
                }},
                {
                decisionsOnCost: {
                    key: DECISIONS_ON_COST_API_DESC,
                    text: DECISIONS_ON_COST,
                    displayed: false,
                    inputType: "text"
                }},
                {
                operativePart: {
                    key: OPERATIVE_PART_API_DESC,
                    text: OPERATIVE_PART,
                    displayed: false,
                    inputType: "text"
                }},
                {
                ecli: {
                    key: ECLI_API_DESC,
                    text: ECLI,
                    displayed: false,
                    inputType: "text"
                }},
                {
                keywords: {
                    key: KEYWORDS_API_DESC,
                    text: KEYWORDS,
                    displayed: false,
                    inputType: "text"
                }
            }
            ],
        };

        this.handleInputChange = this.handleInputChange.bind(this);
        this.searchInputChange = this.searchInputChange.bind(this);
        this.handleVisualizationChange = this.handleVisualizationChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.addFilterEntry = this.addFilterEntry.bind(this);
        this.removeFilterEntry = this.removeFilterEntry.bind(this);
    }

    searchInputChange(event) {
        const target = event.target;
        const value = target.value;
        const name = target.name;
        // this.modifySearchArray(name, value);

        this.handleInputChange(event);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;
        this.setState({
            [name]: value
        });
    }

    modifySearchArray(name, value) {
        // add element to search array on new input
        if (!this.state.elementsToSearchFor.includes(name) && value !== "") {
            let array = this.state.elementsToSearchFor;
            array.push(name);
            this.setState({elementsToSearchFor: array});
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
        // alert('A search was submitted: \n' + alertString);
        event.preventDefault();
        this.requestJSON();
    }


    requestJSON() {
        let json = {};

        json.language = this.getSelectedLanguage();
        // json.corpus = this.getSearchInputValues();
        json.corpus = this.getFilterValues();
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

    // deprecated, need to copy pasta date function later
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

    getFilterValues() {
        let filterEntries = this.state.filterEntries;
        let corpus = [];
        let date = this.getDateForSearch();

        for (const input of filterEntries) {
            let operator = this.getOperatorFromItem(input);

            if (input.key === 'startDate' || input.key === 'endDate') {
                continue;
            }

            let entry = {
                column: input.key,
                value: this.state[input.key],
                operator: operator
            }

            if (entry.value.trim() !== "") {
                corpus.push(entry);
            }
        }

        if (date !== null) {
            corpus.push(date);
        }
        return corpus;
    }

    getOperatorFromItem(item) {
        if (item.hasOwnProperty('operator')) {
            return item.operator
        } else {
            return "";
        }
    }

    getDateForSearch() {
        let startDate, endDate;

        if (this.state.startDate === "" && this.state.endDate === "") {
            return null;
        }

        if (this.state.startDate !== "") {
            startDate = this.state.startDate;
        } else {
            let tempDate = new Date("January 01, 1500 00:00:00");
            let month = tempDate.getMonth() + 1; // months start at index 0 (january = 0)
            startDate = tempDate.getFullYear() + "-" + month + "-" + tempDate.getDate();
        }

        if (this.state.endDate !== "") {
            endDate = this.state.endDate;
        } else {
            let tempDate = new Date(Date.now());
            let month = tempDate.getMonth() + 1;
            endDate = tempDate.getFullYear() + "-" + month + "-" + tempDate.getDate();
            console.debug(tempDate.getMonth());
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


    addFilterEntry(index) {
        let array = this.state.filterEntries;
        let elements = this.state.searchFilterElements;
        // array.push(<FilterEntry elements={elements} index={index} text={text} onChange={this.searchInputChange} onDelete={this.removeFilterEntry}/>);
        if (elements[index][Object.keys(elements[index])].key === 'date') {
            let startDate = {
                key: 'startDate',
                text: 'Start Date',
                displayed: false,
                inputType: 'date'
            };
            let endDate = {
                key: 'endDate',
                text: 'End Date',
                displayed: false,
                inputType: 'date'
            };
            array.push(startDate);
            array.push(endDate);
            this.setState({filterEntries: array});
            return;
        }
        array.push(elements[index][Object.keys(elements[index])]);
        this.setState({filterEntries: array});
    }

    removeFilterEntry(item) {
        let array = this.state.filterEntries;
        for (let i = 0; i < array.length; i++) {
            if (array[i] === item) {
                array.splice(i, 1);
                this.setState({filterEntries: array});
            }
        }
    }

    setOperatorEntry(item) {
        let array = this.state.filterEntries;
        for (let element of array) {
            if (element.key.localeCompare(item.key) === 0) {
                if (element.hasOwnProperty('operator')) {
                    if (element.operator === 'NOT') {
                        element.operator = '';
                    } else {
                        element.operator = 'NOT';
                    }
                } else {
                    element.operator = 'NOT';
                }
            }
        }
        this.setState({filterEntries: array});
    }

    itemIsNegated(item) {
        if (item.hasOwnProperty('operator')) {
            if (item.operator === 'NOT') {
                return true;
            }
        }
        return false;
    }

    getItemNegationClassName(item) {
        if (item.hasOwnProperty('operator')) {
            if (item.operator === 'NOT') {
                return "negation-selector negated-true";
            }
        }
        return "negation-selector negated-false";
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        // put debug logs for states here if needed
        console.debug(this.state);
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
                    <div className="col-70">
                        <input type="text" name="quickSearch" id="quickSearch" className="input-large"
                               onChange={this.searchInputChange}/>
                    </div>
                </div>

                <div className="row">
                    <div className="col-25">
                        <label htmlFor="language" className="search-label">Language</label>
                    </div>
                    <div className="col-70">
                        <select name="language" id="language" className="input-large" onChange={this.searchInputChange}>
                            <option value="english">English</option>
                            <option value="german">German</option>
                        </select>
                    </div>

                </div>

                <div className="row additional-filter-container" id="additional-filter-container">
                    {/*{this.state.filterEntries}*/}
                    <FilterEntryParent
                        data={this.state.filterEntries}
                        getNegationIconClass={(item) => this.getItemNegationClassName(item)}
                        onChange={this.searchInputChange}
                        onDelete={(item) => this.removeFilterEntry(item)}
                        onSetOperator={(item) => this.setOperatorEntry(item)}
                    />
                </div>

                <div className="row dropdown">
                    {/*<div id="filter-dropdown" className="dropdown-content">*/}
                    {/*    /!* Programatically add filter options here *!/*/}
                    {/*</div>*/}
                    {/*<a className="generic-button dropdown" id="add-filter-button" onClick={() => {this.showDropdownContent()}}>+ Filter</a>*/}
                    <DropdownParent
                        data={this.state.searchFilterElements}
                        addFilterEntry={this.addFilterEntry}
                        elements={this.state.filterEntries}
                    />
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
                                <select className="input-large" name={N_GRAM_VISUALIZATION} id={N_GRAM_VISUALIZATION}
                                        onChange={this.handleVisualizationChange}>
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
                                <input type="checkbox" name="tokenRemoveStopWords" id="tokenRemoveStopWords"
                                       className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>
                        <div className={"row"} style={{display: tokensHidden}}>
                            <div className="col-50">
                                <label htmlFor={"tokenRemovePunctuation"}>Remove Punctuation: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="tokenRemovePunctuation" id="tokenRemovePunctuation"
                                       className="input-large"
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
                                <select className="input-large" name={TOKEN_VISUALIZATION} id={TOKEN_VISUALIZATION}
                                        onChange={this.handleVisualizationChange}>
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
                                <input type="checkbox" name="wordCountRemoveStopWords" id="wordCountRemoveStopWords"
                                       className="input-large"
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
                                <input type="checkbox" name="mostFrequentWordsRemoveStopWords"
                                       id="mostFrequentWordsRemoveStopWords" className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>

                        <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="mostFrequentWordsLemmatise">Lemmatise: </label>
                            </div>
                            <div className="col-50">
                                <input type="checkbox" name="mostFrequentWordsLemmatise" id="mostFrequentWordsLemmatise"
                                       className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>
                        </div>

                        <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                            <div className="col-50">
                                <label htmlFor="mostFrequentWordsLimit">Limit: </label>
                            </div>
                            <div className="col-50">
                                <input type="number" name="mostFrequentWordsLimit" id="mostFrequentWordsLimit"
                                       className="input-large"
                                       onChange={this.handleInputChange}/>
                            </div>

                            <div className={"row"} style={{display: this.state.mostFrequentWordsChecked ? '' : 'none'}}>
                                <div className="col-50">
                                    <label htmlFor={MOST_FREQUENT_WORD_VISUALIZATION}>Visualization: </label>
                                </div>
                                <div className="col-50">
                                    <select className="input-large" name={MOST_FREQUENT_WORD_VISUALIZATION}
                                            id={MOST_FREQUENT_WORD_VISUALIZATION}
                                            onChange={this.handleVisualizationChange}>
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