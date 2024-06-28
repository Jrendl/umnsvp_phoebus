import {get} from './helpers';
import ReactJson from 'react-json-view';

function Telemetry(){
    const data = get(`${process.env.REACT_APP_TELEMETRY}/latest`);

    return(
        <ReactJson src={data}/>
    )
}

export default Telemetry;