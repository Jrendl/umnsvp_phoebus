import React from 'react';
import {post, get} from './helpers'

class ModelImport extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            vehiclePath: '',
            racePath: ''
        };


        this.handleChangeVehicle = this.handleChangeVehicle.bind(this);
        this.handleSubmitVehicle = this.handleSubmitVehicle.bind(this);
        this.handleChangeRace = this.handleChangeRace.bind(this);
        this.handleSubmitRace = this.handleSubmitRace.bind(this);
    }

    handleChangeVehicle(e){
        this.setState({vehiclePath: e.target.value});
    }

    handleSubmitVehicle(e){
        post(`${process.env.REACT_APP_GLOBALS}/vehicle_model_path`, this.state.vehiclePath);
        post(`${process.env.REACT_APP_GLOBALS}/import_new_params`, true);
        e.preventDefault();
    }

    handleChangeRace(e){
        this.setState({racePath: e.target.value});
    }

    handleSubmitRace(e){
        post(`${process.env.REACT_APP_GLOBALS}/race_model_path`, this.state.racePath);
        post(`${process.env.REACT_APP_GLOBALS}/import_new_params`, true);
        e.preventDefault();
    }

    render(){
        return(
            <div>
                <form onSubmit={this.handleSubmitVehicle}>
                    <label>
                        Vehicle Model Path:
                        <input type="text" value={this.state.vehiclePath} onChange={this.handleChangeVehicle} />
                    </label>
                    <input type="submit" value="Submit" />
                </form>

                <form onSubmit={this.handleSubmitRace}>
                    <label>
                        Race Model Path:
                        <input type="text" value={this.state.racePath} onChange={this.handleChangeRace} />
                    </label>
                    <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default ModelImport;