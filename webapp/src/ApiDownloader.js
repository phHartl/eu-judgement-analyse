import DataVisualizer from "./DataVisualizer";
import {get} from "react-hook-form";


export async function getResponse(props) {
    const request = new Request("http://127.0.0.1:5000/eu-judgments/api/data", {method: 'POST', body: JSON.stringify(props)});

    const url = request.url;
    const method = request.method;
    const credentials = request.credentials;
    const bodyUsed = request.bodyUsed;

    console.debug(props);

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
        }).catch(error => console.error(error));

    // var http = new XMLHttpRequest();
    // var url = 'http://127.0.0.1:5000/eu-judgments/api/data';
    // http.open('POST', url, true);
    //
    // console.log(props);
    //
    // http.onreadystatechange = function() {//Call a function when the state changes.
    //     if(http.readyState === 4 && http.status === 200) {
    //         alert(http.responseText);
    //     }
    // }
    // http.send(JSON.stringify(props));
}
