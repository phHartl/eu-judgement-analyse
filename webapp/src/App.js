import React from 'react';
import './App.css';
import ReactWordcloud from 'react-wordcloud';
import wordListOne from "./words/words";
import wordListTwo from "./words/words2";
import CanvasJSReact from "./canvasjs.react";

var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            wordList: wordListOne,
            toggle: true,
            rotations: 1,
        }
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <h1>Justice Demo</h1>
                    {this.renderWordcloud()}
                    {this.renderBarChart()}
                </header>
            </div>
        )
    }

    renderWordcloud() {
        return (
            <div className="feature-container">
                <h3 className={"feature-section"}>Wordcloud</h3>
                <div /*style={{border: "1px solid black", paddingBottom: "20px"}} example of how to set inline style*/>
                    <ReactWordcloud
                        words={this.state.toggle ? wordListOne : wordListTwo}
                        options={{
                            fontSizes: [10, 40],
                            rotations: this.state.rotations,
                            /*
                             * If rotations is set to '1', only the first parameter (0) will be used.
                             * If rotations is set to 3+, it will use the parameters that are already given, and evenly divide them for new ones
                             */
                            rotationAngles: [0, 90]
                        }}
                    />
                    <button className={"generic-button"} onClick={() => this.toggleWordsFlag()}>Swap Word Set</button>
                    <button className={"generic-button"} onClick={() => this.toggleRotations()}>Change Rotations ({this.state.rotations})</button>
                </div>
            </div>
        );
    }

    renderBarChart() {
        const options = {
            animationEnabled: true,
            theme: "dark2",
            backgroundColor: "#282c34",
            title:{
                text: "Most Popular Social Networking Sites"
            },
            axisX: {
                title: "Social Network",
                reversed: true,
            },
            axisY: {
                title: "Monthly Active Users",
                includeZero: true,
                labelFormatter: this.addSymbols
            },
            data: [{
                type: "bar",
                dataPoints: [
                    { y:  2200000000, label: "Facebook" },
                    { y:  1800000000, label: "YouTube" },
                    { y:  800000000, label: "Instagram" },
                    { y:  563000000, label: "Qzone" },
                    { y:  376000000, label: "Weibo" },
                    { y:  336000000, label: "Twitter" },
                    { y:  330000000, label: "Reddit" }
                ]
            }]
        }

        return (
            <div className="feature-container" style={{paddingTop: "60px"}}>
                <h3 className={"feature-section"}>Bar Chart</h3>
                <CanvasJSChart options={options}
                               onRef={ref => this.chart = ref}
                />
            </div>
        );
    }

    addSymbols(e){
        var suffixes = ["", "K", "M", "B"];
        var order = Math.max(Math.floor(Math.log(e.value) / Math.log(1000)), 0);
        if(order > suffixes.length - 1)
            order = suffixes.length - 1;
        var suffix = suffixes[order];
        return CanvasJS.formatNumber(e.value / Math.pow(1000, order)) + suffix;
    }

    toggleWordsFlag() {
        this.setState({
            toggle: !this.state.toggle
        })
    }

    toggleRotations() {
        if (this.state.rotations >= 3) {
            this.setState({
                rotations: 1
            })
        } else {
            this.setState({
                rotations: this.state.rotations + 1   // do not use ++
            })
        }
    }

}

export default App;
