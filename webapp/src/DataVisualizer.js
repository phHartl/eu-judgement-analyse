import React from 'react';
import ReactDOM from 'react-dom';
import ReactWordcloud from "react-wordcloud";
import CanvasJSReact from "./canvasjs.react";
import {
    BAR_CHART, COLUMN_CHART,
    DOWNLOAD,
    MOST_FREQUENT_WORD_VISUALIZATION,
    MOST_FREQUENT_WORDS,
    N_GRAMS, NO_DATA_FOUND, POS_TAGS_API_DESC,
    READABILITY,
    READABILITY_API_DESC,
    SENTENCE_COUNT,
    SENTENCE_COUNT_API_DESC,
    TOKEN_COUNT,
    TOKEN_COUNT_API_DESC,
    TOKENS,
    WORD_COUNT,
    WORD_COUNT_API_DESC,
    WORDCLOUD
} from "./Constants";

import 'tippy.js/dist/tippy.css';
import 'tippy.js/animations/scale.css';

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
            tokenCount: false,
            wordCount: false,
            sentenceCount: false,
            rawTableData: false,
            posTags: false,
            posTagsTableData: false
        }
        this.baseState = this.state;
        this.addRawDataToTable = this.addRawDataToTable.bind(this);
        // this.sortDataByParamater = this.sortDataByParamater.bind(this);
    }


    setDataState() {
        let response = this.props.data;
        console.debug(response);
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
        console.debug(key);
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

            case "most frequent words":
                this.setState({mostFrequentWords: true});
                break;

            case "token count":
                this.setState({tokenCount: true});
                this.setState({rawTableData: true});
                break;

            case "word count":
                this.setState({wordCount: true});
                this.setState({rawTableData: true});
                break;

            case "sentence count":
                this.setState({sentenceCount: true});
                this.setState({rawTableData: true});
                break;

            case "pos tags":
                this.setState({posTags: true});
                this.setState({posTagsTableData: true});
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

                <div id={"rawTableData"} style={{display: this.state.rawTableData === false ? 'none' : ''}}>
                    {this.renderRawDataTable()}
                    {this.addRawDataToTable()}
                </div>

                <div id={"readability"} style={{display: this.state.readability === false ? 'none' : ''}}>
                    {this.renderReadability()}
                </div>

                <div id={"nGrams"} style={{visibility: this.state.nGrams !== false}}>
                    {this.renderElement("n-grams", "nGramVisualization", N_GRAMS)}
                </div>

                <div id={"tokens"} style={{visibility: this.state.tokens !== false}}>
                    {this.renderElement('tokens', 'tokenVisualization', TOKENS)}
                </div>

                <div id={"mostFrequentWords"} style={{visibility: this.state.mostFrequentWords !== false}}>
                    {this.renderElement('most frequent words', 'mostFrequentWordVisualization', MOST_FREQUENT_WORDS, "Words")}
                </div>

                <div id={"posTagsTableData"} style={{display: this.state.posTagsTableData === false ? 'none' : ''}}>
                    {this.renderPosTags()}
                    {this.addPosTagsToTable()}
                </div>
            </div>
        )


    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.props.data !== prevProps.data) {
            this.setDataState();
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
            this.insertRawDataTableRow(SENTENCE_COUNT, SENTENCE_COUNT_API_DESC);
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
                this.insertPosTagsTableRow(data)
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
        valueCell.innerHTML = this.props.data[apiKey]

        if (this.props.data[apiKey] === 0) {
            valueCell.innerHTML = NO_DATA_FOUND;
        }
    }

    insertPosTagsTableRow(data) {
        let tableBody = document.getElementById('pos-tags-table-body');

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

    getSortedPosTagsFromData() {
        if (this.props.data.hasOwnProperty(POS_TAGS_API_DESC)) {
            let data = this.props.data[POS_TAGS_API_DESC];
            data = this.groupPosTags(data);

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

    groupPosTags(data) {
        let groupedPosTags = [];
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

    renderReadability() {
        let data = this.getElementsFromResponse(this.props.data[READABILITY_API_DESC], COLUMN_CHART);

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
                return (this.renderBarChart(elements, description, shortDescription));

            case WORDCLOUD:
                elements = this.getElementsFromResponse(this.props.data[element], WORDCLOUD);
                return (this.renderWordcloud(elements, description));

            case DOWNLOAD:
                this.downloadData(this.getElementsFromResponse(this.props.data[element], WORDCLOUD), description);
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

    renderBarChart(words, description, shortDescription = description) {
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
                <CanvasJSChart options={options}
                               onRef={ref => this.chart = ref}
                />
            </div>
        );
    }

    renderWordcloud(words, description) {
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
                            // colors: ["blue", "black"], TODO pos tagging mit farben repräsentieren
                        }}
                    />
                </div>
            </div>
        )
    }

    downloadData(data, description) {
        // initialize a new html element that downloads the values
        // TODO maybe instead render a button that lets the user download on click, instead of instantly downloading?
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
        let dl = document.createElement('a');
        dl.setAttribute('href', dataStr);
        dl.setAttribute("download", description + ".json");
        dl.click();
    }
}

export default DataVisualizer;