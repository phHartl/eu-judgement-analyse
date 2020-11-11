import React from 'react';
import ReactDOM from 'react-dom';
import ReactWordcloud from "react-wordcloud";
import CanvasJSReact from "./canvasjs.react";
import {
    BAR_CHART, COLUMN_CHART,
    DOWNLOAD,
    MOST_FREQUENT_WORD_VISUALIZATION,
    MOST_FREQUENT_WORDS,
    N_GRAMS, NAMED_ENTITIES, NAMED_ENTITIES_API_DESC, NO_DATA_FOUND, POS_TAGS_API_DESC,
    READABILITY,
    READABILITY_API_DESC,
    SENTENCE_COUNT,
    SENTENCE_COUNT_API_DESC, SENTIMENT, SENTIMENT_API_DESC, SIMILARITY, SIMILARITY_API_DESC,
    TOKEN_COUNT,
    TOKEN_COUNT_API_DESC,
    TOKENS, UNIVERSAL_POS_TAGS, UNIVERSAL_POS_TAGS_HINTS,
    WORD_COUNT,
    WORD_COUNT_API_DESC,
    WORDCLOUD
} from "./Constants";

import 'tippy.js/dist/tippy.css';
import 'tippy.js/animations/scale.css';
import DownloadDataButton from "./DownloadDataButton";
import PerDocSelector from "./PerDocSelector";
import PosTagsTableHeader from "./PosTagsTableHeader";
import NamedEntitiesTable from "./NamedEntities/NamedEntitiesTable";

var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;


class DataVisualizer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            dataLoaded: false,
            visualizationInit: false,
            nGrams: false,
            readability: false,
            tokens: false,
            mostFrequentWords: false,
            namedEntities: false,
            tokenCount: false,
            wordCount: false,
            sentenceCount: false,
            rawTableData: false,
            posTags: false,
            posTagsTableData: false,
            readabilityPerDoc: false,
            tokensPerDoc: false,
            posTagsPerDoc: false,
            selectedReadabilityItem: [],
            selectedReadabilityItemValue: [],
            selectedTokensItem: [],
            selectedTokensItemValue: [],
        }
        this.baseState = this.state;
        this.addRawDataToTable = this.addRawDataToTable.bind(this);
        this.handleReadabilityItemSelected = this.handleReadabilityItemSelected.bind(this);
        this.handleTokensItemSelected = this.handleTokensItemSelected.bind(this);
        // this.sortDataByParamater = this.sortDataByParamater.bind(this);
    }


    setDataState() {
        let response = this.props.data;
        this.resetState();
        for (let key in response) {
            if (response.hasOwnProperty(key)) {
                this.setSingleAnalysisState(key);
            }
        }
    }

    resetState() {
        this.setState(this.baseState);
    }

    setSingleAnalysisState(key) {
        switch (key) {
            case "n-grams":
                // this.setState({nGrams: true});
                this.setState({nGrams: true});
                break;

            case "readability":
                this.setState({readability: true});
                break;

            case "tokens":
                this.setState({tokens: true});
                break;

            case "most_frequent_words":
                this.setState({mostFrequentWords: true});
                break;

            case "token_count":
                this.setState({tokenCount: true});
                this.setState({rawTableData: true});
                break;

            case "word_count":
                this.setState({wordCount: true});
                this.setState({rawTableData: true});
                break;

            case "sentence_count":
                this.setState({sentenceCount: true});
                this.setState({rawTableData: true});
                break;

            case "pos_tags":
                this.setState({posTags: true});
                this.setState({posTagsTableData: true});
                break;

            case "readability_per_doc":
                this.setState({readabilityPerDoc: true});
                break;

            case "tokens_per_doc":
                this.setState({tokensPerDoc: true});
                break;

            case "pos_tags_per_doc":
                this.setState({posTagsPerDoc: true});
                break;

            case "sentiment":
                this.setState({sentiment: true});
                this.setState({rawTableData: true});
                break;

            case "similarity":
                this.setState({similarity: true});
                this.setState({rawTableData: true});
                break;

            case "named_entities":
                this.setState({namedEntities: true});
                break;

            default:

        }
        this.setState({visualizationInit: true});
    }


    render() {
        if (this.props.data === '') {
            return null;
        }

        return (
            <div className={"feature-container"} style={{paddingTop: "20px"}}>
                <div>
                    <h2>Analysis Results</h2>
                    <span>
                    <DownloadDataButton
                        description="all results"
                        data={this.props.data}
                        downloadData={(data) => this.downloadData(data, "all_results")}
                    />
                    <a
                        href={"https://eur-lex.europa.eu/legal-content/EN/TXT/?&uri=CELEX:" + this.props.celex}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="generic-button"
                        style={{display: this.props.celex === '' ? 'none' : '', textDecoration: 'none'}}
                    >View Fulltext</a>
                    </span>
                    <div id={"rawTableData"} style={{display: this.state.rawTableData === false ? 'none' : ''}}>
                        <div>
                            {this.renderRawDataTable()}
                        </div>
                        {this.addRawDataToTable()}
                        <div>
                            <DownloadDataButton
                                description={"Data Table"}
                                data={this.getDataFromProps(READABILITY_API_DESC)}
                                downloadData={(data) => this.downloadRawTableData(data, READABILITY)}
                            />
                        </div>
                    </div>

                    <div id={"named-entities"} style={{display: this.state.namedEntities === false ? 'none' : ''}}>
                        <div>
                            {/*{this.renderNamedEntities()}*/}
                            <NamedEntitiesTable data={this.props.data[NAMED_ENTITIES_API_DESC]}/>
                        </div>
                        <div>
                            <DownloadDataButton
                                description={NAMED_ENTITIES}
                                data={this.getDataFromProps(NAMED_ENTITIES_API_DESC)}
                                downloadData={(data) => this.downloadData(data, NAMED_ENTITIES)}
                            />
                        </div>
                    </div>

                    <div id={"readability"} style={{display: this.state.readability === false ? 'none' : ''}}>
                        <div>
                            {this.renderReadability(this.getElementsFromResponse(this.props.data[READABILITY_API_DESC], COLUMN_CHART))}
                        </div>
                        <div>
                            <DownloadDataButton
                                description={READABILITY}
                                data={this.getDataFromProps(READABILITY_API_DESC)}
                                downloadData={(data) => this.downloadData(data, READABILITY)}
                            />
                        </div>
                    </div>

                    <div id={"nGrams"} style={{display: this.state.nGrams === false ? 'none' : ''}}>
                        {this.renderElement("n-grams", "nGramVisualization", N_GRAMS)}
                    </div>

                    <div id={"tokens"} style={{display: this.state.tokens === false ? 'none' : ''}}>
                        {this.renderElement('tokens', 'tokenVisualization', TOKENS)}
                    </div>

                    <div id={"mostFrequentWords"}
                         style={{display: this.state.mostFrequentWords === false ? 'none' : ''}}>
                        <div>
                            {this.renderElement('most_frequent_words', 'mostFrequentWordVisualization', MOST_FREQUENT_WORDS, "Words")}
                        </div>
                    </div>

                    <div id={"posTagsTableData"} style={{display: this.state.posTagsTableData === false ? 'none' : ''}}>
                        <div>
                            {this.renderPosTags()}
                        </div>
                        {this.addPosTagsToTable()}
                        <div>
                            <DownloadDataButton
                                description="PoS-Tags"
                                data={this.getDataFromProps(POS_TAGS_API_DESC)}
                                downloadData={(data) => this.downloadData(data, "pos_tags")}
                            />
                        </div>
                    </div>

                    <div className="row search-option-container">
                        <div id={"readabilityPerDoc"}
                             style={{display: this.state.readabilityPerDoc === false ? 'none' : ''}}>
                            <div>
                                <PerDocSelector
                                    data={this.getDataFromProps("readability_per_doc")}
                                    onChange={this.handleReadabilityItemSelected}
                                    onOptionSelected={function () {
                                    }}
                                    id={"readabilitySelector"}
                                    celexNumbers={this.props.data['celex_numbers']}
                                />
                            </div>
                            <div>
                                {this.renderReadability(this.state.selectedReadabilityItemValue)}
                            </div>
                            <div>
                                <DownloadDataButton
                                    description={READABILITY}
                                    data={this.getDataFromProps("readability_per_doc")}
                                    downloadData={(data) => this.downloadData(data, READABILITY)}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="row search-option-container">
                        <div id={"tokensPerDoc"}
                             style={{display: this.state.tokensPerDoc === false ? 'none' : ''}}>
                            <div>
                                <span className="row">
                                     <h5 style={{display: "inline-block", paddingRight: "20px"}}>Select Document (CELEX):</h5>
                                <PerDocSelector
                                    data={this.getDataFromProps("tokens_per_doc")}
                                    onChange={function () {
                                    }}
                                    onOptionSelected={this.handleTokensItemSelected}
                                    id={"tokenSelector"}
                                    celexNumbers={this.props.data['celex_numbers']}
                                />
                                </span>
                            </div>
                            <div>
                                {this.renderPerDocElement(this.state.selectedTokensItemValue,
                                    TOKENS + " of selected document",
                                    "tokenVisualization",
                                    "tokens_per_doc"
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="row search-option-container">
                        <div id={"posTagsPerDoc"}
                             style={{display: this.state.posTagsPerDoc === false ? 'none' : ''}}>
                            <div>
                                {this.renderPosTagsPerDoc()}
                            </div>
                            {this.addPosTagsPerDocToTable()}
                            <div>
                                <DownloadDataButton
                                    description="PoS-Tags"
                                    data={this.getDataFromProps('pos_tags_per_doc')}
                                    downloadData={(data) => this.downloadData(data, "pos_tags")}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )


    }

    sanitizeReadabilityPerDocData(data) {
        let returnVal = [];
        let entry;
        if (data.length === 0) {
            entry = {
                x: 1,
                y: 0
            }
        } else {
            entry = {
                x: 1,
                y: parseFloat(data)
            }
        }

        returnVal.push(entry);
        console.debug(returnVal);
        this.setState({selectedReadabilityItemValue: returnVal});

    }

    sanitizeTokensPerDocData(data) {
        let returnData = [];
        let visualization = this.props.tokenVisualization;

        for (const word of data) {
            let entry = {};
            switch (visualization) {
                case WORDCLOUD:
                    entry = {
                        text: word[0],
                        value: word[1]
                    }
                    break;

                case BAR_CHART:
                    entry = {
                        y: word[1],
                        label: word[0]
                    }
                    break;

                case COLUMN_CHART:
                    entry = {
                        x: 1,
                        y: word
                    }
                    break;

                default:

            }

            returnData.push(entry);
        }

        this.setState({selectedReadabilityItemValue: returnData});
    }

    handleTokensItemSelected(key) {
        let tokensPerDoc = this.props.data['tokens_per_doc'];
        console.debug(tokensPerDoc);
        console.debug(tokensPerDoc[key]);
        this.setState({selectedTokensItemValue: tokensPerDoc[key]})
    }

    handleReadabilityItemSelected(event) {
        if (event === null) {
            let selector = document.getElementById("readabilitySelector-0");

            if (selector.value === undefined || selector.value === null) {
                return;
            }

            let tempValue = selector.value;

            this.setState({selectedReadabilityItem: tempValue});
            this.sanitizeReadabilityPerDocData(tempValue);
            return;
        }

        const target = event.target;
        const value = target.value;


        this.setState({selectedReadabilityItem: value});
        this.sanitizeReadabilityPerDocData(value);
    }

    setPerDocSelectedItem(analysisName) {
        switch (analysisName) {
            case "readability":

                break;
            default:

        }
    }

    getDataFromProps(identifier) {
        if (!this.props.data.hasOwnProperty(identifier)) {
            return null;
        }

        return this.props.data[identifier];
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.props.data !== prevProps.data) {
            this.setDataState();
        }

        if (this.state.tokensPerDoc && !prevState.tokensPerDoc) {
            this.handleTokensItemSelected(0);
        }

        if (this.state.readabilityPerDoc && !prevState.readabilityPerDoc) {
            this.handleReadabilityItemSelected(null);
        }
    }

    addRawDataToTable() {
        if (this.state.rawTableData) {
            this.deleteOldRows('raw-data-table-body');
        }

        if (this.state.tokenCount) {
            this.insertRawDataTableRow(TOKEN_COUNT, TOKEN_COUNT_API_DESC);
        }

        if (this.state.wordCount) {
            this.insertRawDataTableRow(WORD_COUNT, WORD_COUNT_API_DESC);
        }

        if (this.state.sentenceCount) {
            this.insertRawDataTableRow(SENTENCE_COUNT, SENTIMENT_API_DESC);
        }

        if (this.state.sentiment) {
            this.insertRawDataTableRow(SENTIMENT, SENTIMENT_API_DESC);
        }

        if (this.state.similarity) {
            this.insertRawDataTableRow(SIMILARITY, SIMILARITY_API_DESC);
        }

    }

    addPosTagsPerDocToTable() {
        if (this.state.posTagsPerDoc) {
            let data = this.getPosTagsPerDocFromData();
            if (data === null) {
                return;
            }

            this.deleteOldRows('pos-tags-per-doc-table-body')
            this.insertPosTagsPerDocTableRow(data);
        }

    }

    addPosTagsToTable() {
        if (this.state.posTagsTableData) {
            let data = this.getSortedPosTagsFromData();
            if (data === null) {
                return;
            }

            if (this.state.posTagsTableData) {
                this.deleteOldRows('pos-tags-table-body');
                this.insertPosTagsTableRow(data);
            }
        }
    }

    deleteOldRows(tableId) {
        let tableBody = document.getElementById(tableId);

        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild);
        }
    }

    insertRawDataTableRow(description, apiKey) {
        let tableBody = document.getElementById('raw-data-table-body');
        let row = tableBody.insertRow(0);
        let typeCell = row.insertCell(0);
        let valueCell = row.insertCell(1);

        typeCell.innerHTML = description;
        valueCell.innerHTML = this.props.data[apiKey];

        if (description === SENTIMENT) {
            let value;
            switch (this.props.data[apiKey]) {
                case 0:
                    value = "Negative";
                    break;

                case 1:
                    value = "Neutral";
                    break;

                case 2:
                    value = "Positive";
                    break;

                default:
                    value = "No value found"
            }
            valueCell.innerHTML = value;
        }

        if (description === SIMILARITY) {
            if (this.props.data[apiKey] === -1) {
                valueCell.innerHTML = "Error: Can only compare exactly two documents"
            }
        }

        if (this.props.data[apiKey] === 0) {
            valueCell.innerHTML = NO_DATA_FOUND;
        }
    }

    insertPosTagsTableRow(data) {
        let tableBody = document.getElementById('pos-tags-table-body');

        if (data === null) {
            let row = tableBody.insertRow(0);
            let cell = row.insertCell(0);

            cell.innerHTML = "No data found";
        }

        for (let i = 0; i < data.length; i++) {
            let row = tableBody.insertRow(0);
            let tokenCell = row.insertCell(0);
            let tagCell = row.insertCell(1);
            let countCell = row.insertCell(2);

            tokenCell.innerHTML = data[i].token;
            tagCell.innerHTML = data[i].posTag;
            countCell.innerHTML = data[i].count;
        }
    }

    insertPosTagsPerDocTableRow(data) {
        let tableBody = document.getElementById('pos-tags-per-doc-table-body');

        if (data === null) {
            let row = tableBody.insertRow(0);
            let cell = row.insertCell(0);

            cell.innerHTML = "No data found";
        }

        for (let i = 0; i < data.length; i++) {
            let row = tableBody.insertRow(0);

            // cell that contains the celex number of the coument as a link
            let documentCell = row.insertCell(0);
            documentCell.classList.add("pos-tags-document-cell");

            // create the link and add it to the table cell
            let documentLink = document.createElement("a");
            documentLink.classList.add("pos-tags-document-link");
            documentLink.innerHTML = this.props.data['celex_numbers'][i];
            documentLink.setAttribute("href",
                "https://eur-lex.europa.eu/legal-content/EN/TXT/?&uri=CELEX:" + this.props.data['celex_numbers'][i]);
            documentLink.setAttribute("target", "_blank");

            documentCell.appendChild(documentLink);


            // add the counted tag appearances to the table
            for (let j = 0; j < UNIVERSAL_POS_TAGS.length; j++) {
                let tagCell = row.insertCell(j + 1);
                tagCell.classList.add("pos-tags-per-doc-cell");
                if (data[i].tags[j] !== undefined) {
                    tagCell.innerHTML = data[i].tags[j]['count'];
                } else {
                    tagCell.innerHTML = "" + 0;
                }

            }
        }
    }

    renderPosTags() {

        return (
            <div className="feature-section">
                <h3>Part of Speech Tags</h3>
                <div className="limiter">
                    <div className="container-table100">
                        <div className="wrap-table100">
                            <div className="table100">
                                <table id="pos-tags-table">
                                    <thead>
                                    <tr>
                                        <th>Token</th>
                                        <th>Tag</th>
                                        <th>Count</th>
                                    </tr>
                                    </thead>
                                    <tbody id="pos-tags-table-body">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        )
    }

    renderPosTagsPerDoc() {
        return (
            <div className="feature-section">
                <h3>Part of Speech Tags</h3>
                <div className="limiter">
                    <div className="container-table100">
                        <div className="wrap-table100">
                            <div className="table100">
                                <table id="pos-tags-per-doc-table">
                                    <thead>
                                    <tr>
                                        <th className="pos-tags-per-doc-header" title="CELEX-Number of Document">
                                            Document
                                        </th>
                                        <PosTagsTableHeader/>
                                    </tr>
                                    </thead>
                                    <tbody id="pos-tags-per-doc-table-body">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        )
    }

    getSortedPosTagsFromData() {
        if (this.props.data.hasOwnProperty(POS_TAGS_API_DESC)) {
            let data = this.props.data[POS_TAGS_API_DESC];
            data = this.groupPosTagsByToken(data);

            if (data === null) {
                return null;
            }

            // sort pos-tag data by count, with highest count at index[0]
            data = data.sort(function (a, b) {
                    if (a.count > b.count) {
                        return 1;
                    } else if (a.count < b.count) {
                        return -1;
                    }
                    return 0;
                }
            );
            return data;
        }
        return null;
    }

    getPosTagsPerDocFromData() {
        if (this.props.data.hasOwnProperty('pos_tags_per_doc')) {
            let data = this.props.data['pos_tags_per_doc'];
            data = this.groupPosTagsByTag(data);

            if (data === null) {
                return null;
            }

            for (const document of data) {
                let tags = document.tags;
                tags.sort(function (a, b) {
                    return a.posTag.localeCompare(b.posTag);
                })
            }

            return data;
        }
        return null;
    }

    groupPosTagsByTag(data) {
        let groupedPosTags = []
        if (data === null) {
            return null;
        }

        for (let i = 0; i < data.length; i++) {
            let document = data[i];
            let tags = [];
            let entry = {
                document: this.props.data['celex_numbers'][i],
                tags: tags
            }

            for (const tag of UNIVERSAL_POS_TAGS) {
                let tagEntry = {
                    posTag: tag,
                    count: 0
                }
                tags.push(tagEntry);
            }


            for (const tag of document) {
                let tagEntry = {
                    posTag: tag[1],
                    count: 1
                }
                if (tags.some(item => item.posTag === tagEntry.posTag)) {
                    for (const existingEntry of tags) {
                        if (existingEntry.posTag === tagEntry.posTag) {
                            tags[tags.indexOf(existingEntry)].count = existingEntry.count + 1;
                        }
                    }
                } else {
                    tags.push(tagEntry)
                }
            }
            groupedPosTags.push(entry);
        }
        return groupedPosTags;
    }

    groupPosTagsByToken(data) {
        let groupedPosTags = [];
        if (data === null) {
            return null;
        }
        for (const tag of data) {
            let entry = {
                token: tag[0],
                posTag: tag[1],
                count: 1
            }
            if (groupedPosTags.some(item => item.token === entry.token && item.posTag === entry.posTag)) {
                for (const existingEntry of groupedPosTags) {
                    if (existingEntry.token === entry.token && existingEntry.posTag === entry.posTag) {
                        groupedPosTags[groupedPosTags.indexOf(existingEntry)].count = existingEntry.count + 1;
                    }
                }
            } else {
                groupedPosTags.push(entry)
            }
        }
        return groupedPosTags;
    }

    renderRawDataTable() {
        return (
            <div className="feature-section">
                <h3>Data Table</h3>
                <div className="limiter">
                    <div className="container-table100">
                        <div className="wrap-table100">
                            <div className="table100">
                                <table id="raw-data-table">
                                    <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Value</th>
                                    </tr>
                                    </thead>
                                    <tbody id="raw-data-table-body">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        )
    }

    renderReadability(data) {

        const options = {
            animationEnabled: true,
            exportEnabled: true,
            theme: "dark2", //"light1", "dark1", "dark2"
            backgroundColor: null,
            title: {
                text: READABILITY
            },
            axisX: {
                labelFormatter: function () {
                    return "";
                }
            },
            axisY: {
                includeZero: true,
                interval: 10,
                viewportMinimum: 0,
                viewportMaximum: 100,
                labelFormatter: function (e) {
                    switch (e.value) {
                        case 10:
                            return "Extremely difficult to read (10)"
                        case 30:
                            return "Very difficult to read (30)"
                        case 50:
                            return "Difficult to read (50)"
                        case 60:
                            return "Fairly difficult to read (60)"
                        case 70:
                            return "Plain English (70)"
                        case 80:
                            return "Fairly easy to read (80)"
                        case 90:
                            return "Easy to read (90)"
                        case 100:
                            return "Very easy to read (100)"
                        default:
                            return ""
                    }
                }
            },
            data: [{
                type: "column",
                indexLabelFontColor: "#5A5757",
                indexLabelPlacement: "outside",
                dataPoints: data
            }]
        }

        return (
            <div className={"readability-chart"} style={{margin: "auto"}}>
                <CanvasJSChart options={options}
                    /* onRef={ref => this.chart = ref} */
                />
                {/*You can get reference to the chart instance as shown above using onRef. This allows you to access all chart properties and methods*/}
            </div>
        );
    }

    renderNamedEntities() {
        let data = this.props.data[NAMED_ENTITIES_API_DESC];

        for (const entry of data) {
            console.debug(entry);

        }

        return null;
    }

    renderElement(element, elementVisualization, description, shortDescription = description) {
        if (!this.props.data.hasOwnProperty(element)) {
            return null;
        }

        console.log(this.props.data[element]);
        if (this.props.data[element] === undefined || this.props.data[element].length === 0) {
            return (
                <div>
                    <div className="row">
                        <h3 className="col-100">{description}</h3>
                    </div>
                    <div className="row">
                        <h5>{NO_DATA_FOUND}</h5>
                    </div>
                </div>
            )
        }

        let visualization = this.props[elementVisualization];
        let elements = "";

        switch (visualization) {
            case BAR_CHART:
                elements = this.getElementsFromResponse(this.props.data[element], BAR_CHART);
                return (this.renderBarChart(elements, description, shortDescription, element));

            case WORDCLOUD:
                elements = this.getElementsFromResponse(this.props.data[element], WORDCLOUD);
                return (this.renderWordcloud(elements, description, element));

            case DOWNLOAD:
                this.downloadData(this.getElementsFromResponse(this.props.data[element], WORDCLOUD), description);
                break;

            default:
                return null;
        }
    }

    renderPerDocElement(values, description, elementVisualization, elementDescription) {
        let visualization = this.props[elementVisualization];
        let elements = "";

        switch (visualization) {
            case BAR_CHART:
                elements = this.getElementsFromResponse(values, BAR_CHART);
                return (this.renderBarChart(elements, description, description, elementDescription));

            case WORDCLOUD:
                elements = this.getElementsFromResponse(values, WORDCLOUD);
                return (this.renderWordcloud(elements, description, elementDescription));

            case DOWNLOAD:
                this.downloadData(this.getElementsFromResponse(elements, WORDCLOUD), description);
                break;

            default:
                return null;
        }
    }


    // sort the elements from the response body into arrays that the visualization libraries can read
    getElementsFromResponse(array, visualization) {
        let returnData = [];
        if (!this.isIterable(array)) {
            let value = array;
            array = [value];
        }

        for (const word of array) {
            let entry = {};
            switch (visualization) {
                case WORDCLOUD:
                    entry = {
                        text: word[0],
                        value: word[1]
                    }
                    break;

                case BAR_CHART:
                    entry = {
                        y: word[1],
                        label: word[0]
                    }
                    break;

                case COLUMN_CHART:
                    entry = {
                        x: 1,
                        y: word
                    }
                    break;

                default:

            }

            returnData.push(entry);
        }
        return returnData;
    }

    isIterable(object) {
        if (object == null) {
            return false;
        }
        return typeof object[Symbol.iterator] === 'function';

    }

    renderBarChart(words, description, shortDescription = description, element) {
        const options = {
            animationEnabled: true,
            theme: "dark2",
            backgroundColor: "#282c34",
            title: {
                text: description
            },
            axisX: {
                title: shortDescription,
                reversed: true,
            },
            axisY: {
                title: "Count",
                includeZero: true,
                labelFormatter: this.addSymbols
            },
            data: [{
                type: "bar",
                dataPoints: words
            }]
        }

        return (
            <div>
                <div>
                    <CanvasJSChart options={options}
                                   onRef={ref => this.chart = ref}
                    />
                </div>
                <div>
                    <DownloadDataButton
                        description={description}
                        data={this.getDataFromProps(element)}
                        downloadData={(data) => this.downloadData(data, description)}
                    />
                </div>
            </div>
        );
    }

    renderWordcloud(words, description, element) {
        return (
            <div>
                <h3 className={"feature-section"}>{description}</h3>
                <div>
                    <ReactWordcloud
                        words={words}
                        maxWords={500}
                        options={{
                            fontSizes: [15, 40],
                            rotations: 1,
                            tooltipOptions: {
                                theme: "light-border"
                            },
                            rotationAngles: [0]
                            // colors: ["blue", "black"],
                        }}
                    />
                </div>
                <div>
                    <DownloadDataButton
                        description={description}
                        data={this.getDataFromProps(element)}
                        downloadData={(data) => this.downloadData(data, description)}
                    />
                </div>
            </div>
        )
    }

    downloadData(data, description) {
        // initialize a new html element that downloads the values
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
        let dl = document.createElement('a');
        dl.setAttribute('href', dataStr);
        dl.setAttribute("download", description + ".json");
        dl.click();
    }

    downloadRawTableData() {
        let data = {};
        if (this.state.tokenCount) {
            data.tokenCount = this.props.data[TOKEN_COUNT_API_DESC];
        }

        if (this.state.wordCount) {
            data.wordCount = this.props.data[WORD_COUNT_API_DESC];
        }

        if (this.state.sentenceCount) {
            data.sentenceCount = this.props.data[SENTENCE_COUNT_API_DESC];
        }

        console.debug(data);

        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
        let dl = document.createElement('a');
        dl.setAttribute('href', dataStr);
        dl.setAttribute("download", "raw_data.json");
        dl.click();
    }


}

export default DataVisualizer;