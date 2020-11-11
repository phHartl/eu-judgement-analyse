import React from 'react';
import {usePromiseTracker} from "react-promise-tracker";
import Loader from 'react-loader-spinner';

export const LoadingIndicator = () => {
    const {promiseInProgress} = usePromiseTracker();
    return (
        promiseInProgress &&

            <div
                style = {{
                    width: "100%",
                    height: "100",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center"
                }}
                >
                <Loader type={"ThreeDots"} color={"lightgray"} height={"100"} width={"100"} />
            </div>
    )
}

