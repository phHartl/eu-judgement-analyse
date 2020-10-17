import React from 'react';
import {
    APPLICANT,
    APPLICANT_API_DESC,
    AUTHOR,
    AUTHOR_API_DESC,
    BAR_CHART,
    CASE_AFFECTING_API_DESC, CASE_LAW_DIRECTORY, CASE_LAW_DIRECTORY_API_DESC,
    CELEX,
    CELEX_API_DESC,
    DATE,
    DATE_API_DESC, DECISIONS_ON_COST,
    DECISIONS_ON_COST_API_DESC, DEFENDANT, DEFENDANT_API_DESC,
    DOWNLOAD, ECLI, ECLI_API_DESC,
    END_DATE_API_DESC, ENDORSEMENTS, ENDORSEMENTS_API_DESC, GROUNDS, GROUNDS_API_DESC, KEYWORDS, KEYWORDS_API_DESC,
    MOST_FREQUENT_WORD_VISUALIZATION, MOST_FREQUENT_WORDS,
    N_GRAM_VISUALIZATION, N_GRAMS, OPERATIVE_PART, OPERATIVE_PART_API_DESC,
    PARTIES,
    PARTIES_API_DESC, POS_TAGS, PROCEDURE_TYPE, PROCEDURE_TYPE_API_DESC, READABILITY, SENTENCE_COUNT, SENTENCES,
    START_DATE_API_DESC,
    SUBJECT,
    SUBJECT_API_DESC, SUBJECT_MATTER, SUBJECT_MATTER_API_DESC,
    TITLE,
    TITLE_API_DESC, TOKEN_COUNT,
    TOKEN_VISUALIZATION, TOKENS, WORD_COUNT,
    WORDCLOUD
} from "./Constants";
import FilterDropdownParent from "./FilterDropdown/FilterDropdownParent";
import FilterEntryParent from "./FilterEntryParent";
import AnalysisOptionsParent from "./Analysis/AnalysisOptionsParent";
import AnalysisDropdownParent from "./AnalysisDropdown/AnalysisDropdownParent";


let requestJSON = "";

class SearchForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            language: "english",
            nGramsOptions: false,
            nLimit: "",
            n: "",
            readabilityOptions: false,
            tokensOptions: false,
            tokenLimit: "",
            tokenCountOptions: false,
            tokenRemoveStopWords: false,
            tokenRemovePunctuation: false,
            wordCountOptions: false,
            wordCountRemoveStopWords: false,
            mostFrequentWordsOptions: false,
            mostFrequentWordsLimit: "",
            mostFrequentWordsRemoveStopWords: false,
            mostFrequentWordsLemmatise: false,
            sentencesOptions: false,
            sentenceCountOptions: false,
            posTagsOptions: false,
            elementsToSearchFor: [],
            startDate: "",
            endDate: "",
            dropdownData: "",
            filterEntries: [],
            filterValues: [],
            currentAddedAnalysisOptions: [],
            analysisOptionsArray: [],
            searchFilterElements: [{
                parties: {
                    key: PARTIES_API_DESC,
                    text: PARTIES,
                    displayed: false,
                    inputType: "text",
                    displaySearchIdentifier: "none"
                }
            },
                {
                    date: {
                        key: DATE_API_DESC,
                        text: DATE,
                        displayed: false,
                        inputType: "date",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    author: {
                        key: AUTHOR_API_DESC,
                        text: AUTHOR,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                },
                {
                    subject: {
                        key: SUBJECT_API_DESC,
                        text: SUBJECT,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    celex: {
                        key: CELEX_API_DESC,
                        text: CELEX,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    title: {
                        key: TITLE_API_DESC,
                        text: TITLE,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    endorsements: {
                        key: ENDORSEMENTS_API_DESC,
                        text: ENDORSEMENTS,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    grounds: {
                        key: GROUNDS_API_DESC,
                        text: GROUNDS,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    decisionsOnCost: {
                        key: DECISIONS_ON_COST_API_DESC,
                        text: DECISIONS_ON_COST,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    operativePart: {
                        key: OPERATIVE_PART_API_DESC,
                        text: OPERATIVE_PART,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    ecli: {
                        key: ECLI_API_DESC,
                        text: ECLI,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    keywords: {
                        key: KEYWORDS_API_DESC,
                        text: KEYWORDS,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: "none"
                    }
                },
                {
                    subjectMatter: {
                        key: SUBJECT_MATTER_API_DESC,
                        text: SUBJECT_MATTER,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                },
                {
                    caseLawDirectory: {
                        key: CASE_LAW_DIRECTORY_API_DESC,
                        text: CASE_LAW_DIRECTORY,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                },
                {
                    applicant: {
                        key: APPLICANT_API_DESC,
                        text: APPLICANT,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                },
                {
                    defendant: {
                        key: DEFENDANT_API_DESC,
                        text: DEFENDANT,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                },
                {
                    procedureType: {
                        key: PROCEDURE_TYPE_API_DESC,
                        text: PROCEDURE_TYPE,
                        displayed: false,
                        inputType: "text",
                        displaySearchIdentifier: ""
                    }
                }
            ],
            analysisOptions: [
                {
                    nGrams: {
                        name: "nGramsOptions",
                        id: "nGramsOptions",
                        description: N_GRAMS,
                        options: [{
                            n: {
                                inputType: "number",
                                description: "N",
                                name: "n"
                            },
                            limit: {
                                inputType: "number",
                                description: "Limit",
                                name: "nOptionsLimit"
                            }
                        }],
                        visualizationOptions: [WORDCLOUD, BAR_CHART, DOWNLOAD]
                    },
                    readability: {
                        name: "readabilityOptions",
                        id: "readabilityOptions",
                        description: READABILITY,
                        options: null,
                        visualizationOptions: null
                    },

                    tokens: {
                        name: "tokensOptions",
                        id: "tokensOptions",
                        description: TOKENS,
                        options: [{
                            removeStopWords: {
                                inputType: "checkbox",
                                description: "Remove Stop Words",
                                name: "tokensOptionsRemoveStopWords"
                            },
                            removePunctuation: {
                                inputType: "checkbox",
                                description: "Remove Punctuation",
                                name: "tokensOptionsRemovePunctuation"
                            },
                            limit: {
                                inputType: "number",
                                description: "Limit",
                                name: "tokensOptionsLimit"
                            }
                        }],
                        visualizationOptions: [WORDCLOUD, BAR_CHART, DOWNLOAD]
                    },

                    tokenCount: {
                        name: "tokenCountOptions",
                        id: "tokenCountOptions",
                        description: TOKEN_COUNT,
                        options: null,
                        visualizationOptions: null
                    },

                    wordCount: {
                        name: "wordCountOptions",
                        id: "wordCountOptions",
                        description: WORD_COUNT,
                        options: [{
                            removeStopWords: {
                                inputType: "checkbox",
                                description: "Remove Stop Words",
                                name: "wordCountOptionsRemoveStopWords"
                            }
                        }],
                        visualizationOptions: null
                    },

                    mostFrequentWords: {
                        name: "mostFrequentWordsOptions",
                        id: "mostFrequentWordsOptions",
                        description: MOST_FREQUENT_WORDS,
                        options: [{
                            removeStopWords: {
                                inputType: "checkbox",
                                description: "Remove Stop Words",
                                name: "mostFrequentWordsOptionsRemoveStopWords"
                            },
                            lemmatise: {
                                inputType: "checkbox",
                                description: "Lemmatise",
                                name: "mostFrequentWordsOptionsLemmatise"
                            },
                            limit: {
                                inputType: "number",
                                description: "Limit",
                                name: "mostFrequentWordsOptionsLimit"
                            }
                        }],
                        visualizationOptions: [WORDCLOUD, BAR_CHART, DOWNLOAD]
                    },

                    sentences: {
                        name: "sentencesOptions",
                        id: "sentencesOptions",
                        description: SENTENCES,
                        options: null,
                        visualizationOptions: null
                    },

                    sentenceCount: {
                        name: "sentenceCountOptions",
                        id: "sentenceCountOptions",
                        description: SENTENCE_COUNT,
                        options: null,
                        visualizationOptions: null
                    },

                    posTags: {
                        name: "posTagsOptions",
                        id: "posTagsOptions",
                        description: POS_TAGS,
                        options: null,
                        visualizationOptions: null
                    }

                }]

        };

        this.handleInputChange = this.handleInputChange.bind(this);
        this.searchInputChange = this.searchInputChange.bind(this);
        this.handleVisualizationChange = this.handleVisualizationChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.addFilterEntry = this.addFilterEntry.bind(this);
        this.removeFilterEntry = this.removeFilterEntry.bind(this);
        this.addAnalysisOptionToDocument = this.addAnalysisOptionToDocument.bind(this);
        this.removeAnalysisOptionFromDocument = this.removeAnalysisOptionFromDocument.bind(this);
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
        if (json.analysis.length === 0) {
            document.getElementById('analysis-hint').setAttribute("style", "color: #b81d1d");
            return;
        }
        this.props.onResponse(json);
        console.debug(json);
    }

    addAnalysisOptionsToJson() {
        let analysisTypes = [];

        for (const element of this.state.currentAddedAnalysisOptions) {
            switch (element.description) {
                case N_GRAMS:
                    if (this.state.n === "") {
                        this.state.n = 2;
                    }

                    analysisTypes.push({
                        type: "n-grams",
                        n: parseInt(this.state.n),
                        limit: parseInt(this.state.nGramsLimit)
                    });

                    break;

                case READABILITY:
                    analysisTypes.push({
                        type: "readability"
                    });
                    break;

                case TOKENS:
                    analysisTypes.push({
                        type: "tokens",
                        "remove stop words": this.state.tokenRemoveStopWords,
                        "remove punctuation": this.state.tokenRemovePunctuation,
                        limit: parseInt(this.state.tokenLimit)
                    });
                    break;

                case MOST_FREQUENT_WORDS:
                    analysisTypes.push({
                        type: "most frequent words",
                        "remove stop words": this.state.mostFrequentWordsRemoveStopWords,
                        lemmatise: this.state.mostFrequentWordsLemmatise,
                        limit: parseInt(this.state.mostFrequentWordsLimit)
                    });
                    break;

                case SENTENCE_COUNT:
                    analysisTypes.push({
                        type: "sentence count"
                    });
                    break;

                case TOKEN_COUNT:
                    analysisTypes.push({
                        type: "token count"
                    })
                    break;

                case WORD_COUNT:
                    analysisTypes.push({
                        type: "word count",
                        "remove stop words": this.state.wordCountRemoveStopWords
                    })
                    break;

                case POS_TAGS:
                    analysisTypes.push({
                        type: "pos tags"
                    })
                    break;

                case SENTENCES:
                    analysisTypes.push({
                        type: "sentences"
                    })
                    break;

                default:
                    console.info("No matching analysis option found.")
            }
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
            let searchIdentifier = this.getSearchIdentifierFromItem(input);

            if (input.key === 'startDate' || input.key === 'endDate') {
                continue;
            }

            let entry = {
                column: input.key,
                value: this.state[input.key],
                "search identifier": searchIdentifier
            }

            if (operator !== "") {
                entry.operator = operator;
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

    getSearchIdentifierFromItem(item) {
        if (item.hasOwnProperty('search identifier')) {
            return item["search identifier"];
        } else {
            return false;
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
                inputType: 'date',
                displaySearchIdentifier: "none"
            };
            let endDate = {
                key: 'endDate',
                text: 'End Date',
                displayed: false,
                inputType: 'date',
                displaySearchIdentifier: "none"
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

    setSearchIdentifier(item) {
        let array = this.state.filterEntries;
        for (let element of array) {
            if (element.key.localeCompare(item.key) === 0) {
                if (element.hasOwnProperty('search identifier')) {
                    element["search identifier"] = !element["search identifier"];
                } else {
                    element["search identifier"] = true;
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

    getSearchIdentifierClass(item) {
        if (item.hasOwnProperty('search identifier')) {
            if (item["search identifier"] === true) {
                return "search-identifier-true";
            }
        }
        return "search-identifier-false";
    }

    getAnalysisOptionsArray() {
        let array = [];
        for (const element in this.state.analysisOptions[0]) {
            array.push(this.state.analysisOptions[0][element]);
        }
        this.setState({analysisOptionsArray: array});
    }

    addAnalysisOptionToDocument(element) {
        let array = this.state.currentAddedAnalysisOptions;

        array.push(element);
        this.setState({currentAddedAnalysisOptions: array});
    }

    removeAnalysisOptionFromDocument(element) {
        console.debug("removing item:");
        let array = this.state.currentAddedAnalysisOptions;
        for (let i = 0; i < array.length; i++) {
            if (array[i] === element) {
                array.splice(i, 1);
                this.setState({currentAddedAnalysisOptions: array});
            }
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        // put debug logs for states here if needed
    }

    componentDidMount() {
        this.getAnalysisOptionsArray();
    }


    render() {

        return (
            <form className="feature-container" onSubmit={this.handleSubmit}>
                <div className="row search-option-container">
                    <h3 className="col-100">Search Filter</h3>
                    <div className="row filter-entry">
                        <div className="col-25">
                            <label htmlFor="quickSearch" className="search-label">Quick Search</label>
                        </div>
                        <div className="col-70">
                            <input type="text" name="quickSearch" id="quickSearch" className="input-large"
                                   onChange={this.searchInputChange}/>
                        </div>
                    </div>

                    <div className="row filter-entry">
                        <div className="col-25">
                            <label htmlFor="language" className="search-label">Language</label>
                        </div>
                        <div className="col-70">
                            <select name="language" id="language" className="input-large"
                                    onChange={this.searchInputChange}>
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
                            getSearchIdentifierClass={(item) => this.getSearchIdentifierClass(item)}
                            onChange={this.searchInputChange}
                            onDelete={(item) => this.removeFilterEntry(item)}
                            onSetOperator={(item) => this.setOperatorEntry(item)}
                            onSetSearchIdentifier={(item) => this.setSearchIdentifier(item)}
                        />
                    </div>

                    <div className="row">
                        {/*<div id="filter-dropdown" className="dropdown-content">*/}
                        {/*    /!* Programatically add filter options here *!/*/}
                        {/*</div>*/}
                        {/*<a className="generic-button dropdown" id="add-filter-button" onClick={() => {this.showDropdownContent()}}>+ Filter</a>*/}
                        <div className="col-100">
                            <FilterDropdownParent
                                data={this.state.searchFilterElements}
                                addFilterEntry={this.addFilterEntry}
                                elements={this.state.filterEntries}
                            />
                        </div>
                    </div>
                </div>

                <div className="row search-option-container" style={{marginTop:"20px"}}>
                    <h3 className="col-100">Analysis Options</h3>

                    <div className="row">
                        <AnalysisDropdownParent
                            data={this.state.analysisOptions}
                            alreadyAdded={this.state.currentAddedAnalysisOptions}
                            addAnalysisOption={this.addAnalysisOptionToDocument}
                        />
                    </div>

                    <div className="row">
                        <AnalysisOptionsParent
                            data={this.state.currentAddedAnalysisOptions}
                            handleInputChange={this.handleInputChange}
                            handleVisualizationChange={this.handleVisualizationChange}
                            removeAnalysisOptionFromDocument={(item) => this.removeAnalysisOptionFromDocument(item)}
                        />
                    </div>
                </div>


                <div className="row">
                    <input type="submit" name="submit-search" id="submit-search"
                           />
                </div>
            </form>
        );
    }
}


export default SearchForm;