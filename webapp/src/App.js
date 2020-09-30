import React from 'react';
import './App.css';
import ReactWordcloud from 'react-wordcloud';
import CanvasJSReact from "./canvasjs.react";
import SearchForm from "./SearchForm";
import DataVisualizer from "./DataVisualizer";
import {
    BAR_CHART,
    MOST_FREQUENT_WORD_VISUALIZATION,
    N_GRAM_VISUALIZATION,
    TOKEN_VISUALIZATION,
    WORDCLOUD
} from "./Constants";
import {usePromiseTracker} from "react-promise-tracker";
import {LoadingIndicator} from "./LoadingIndicator";
import {trackPromise} from "react-promise-tracker";


var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;


class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: false,
            // dataFetched: false,
            data: '',
            nGramVisualization: BAR_CHART,
            tokenVisualization: WORDCLOUD,
            mostFrequentWordVisualization: BAR_CHART,
        }
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleVisualizationSelected = this.handleVisualizationSelected.bind(this);
    }


    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <h1>Justice Demo</h1>
                    <SearchForm
                        // dataFetched={this.state.dataFetched}
                        data={this.state.data}
                        onResponse={json => this.handleFormSubmit(json)}
                        onVisualizationSelected={(name, value) => this.handleVisualizationSelected(name, value)}
                    />
                    <LoadingIndicator/>
                    <div id="error-message" name="error-message" style={{display: this.state.error === true ? "" : "none"}}>
                        <h4>There was an error when fetching your data. Please check your inputs or try again later.</h4>
                    </div>
                    <DataVisualizer
                        // dataFetched={this.state.dataFetched}
                        data={this.state.data}
                        nGramVisualization={this.state.nGramVisualization}
                        tokenVisualization={this.state.tokenVisualization}
                        mostFrequentWordVisualization={this.state.mostFrequentWordVisualization}
                    />
                    {/*{this.renderDemoWordcloud()}*/}
                    {/*{this.renderBarChart()}*/}
                </header>
            </div>
        )
    }

    handleVisualizationSelected(name, value) {
        switch (name) {
            case N_GRAM_VISUALIZATION:
                this.setState(() => {
                    return {nGramVisualization: value}
                });
                break;

            case TOKEN_VISUALIZATION:
                this.setState(() => {
                    return {tokenVisualization: value}
                });
                break;

            case MOST_FREQUENT_WORD_VISUALIZATION:
                this.setState(() => {
                    return {mostFrequentWordVisualization: value}
                });
                break;

            default:
                return;
        }
    }


    handleFormSubmit(json) {
        this.downloadData(json);

    }

    downloadData(json) {
        const request = new Request("http://127.0.0.1:5000/eu-judgments/api/data", {
            method: 'POST',
            body: JSON.stringify(json)
        });

        trackPromise(
            fetch(request)
                .then(response => {
                    if (response.status === 200) {
                        return response.json();
                    } else {
                        throw new Error('Error when requesting data from the API server.');
                    }
                })
                .then(response => {
                    console.debug(response);
                    this.setState({error: false});
                    this.setState({data: response});
                    // this.setState({dataFetched: true});
                }).catch(error => {
                    console.error(error);
                    this.setState({error: true});
            }));

    }

    addSymbols(e) {
        var suffixes = ["", "K", "M", "B"];
        var order = Math.max(Math.floor(Math.log(e.value) / Math.log(1000)), 0);
        if (order > suffixes.length - 1)
            order = suffixes.length - 1;
        var suffix = suffixes[order];
        return CanvasJS.formatNumber(e.value / Math.pow(1000, order)) + suffix;
    }

}

export default App;
