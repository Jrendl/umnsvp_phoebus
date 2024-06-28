import React from 'react';
import {post, get} from './helpers'

class SDCardParser extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            outPath: '',
            SDCardPath: ''
        };


        this.handleChangeOut = this.handleChangeOut.bind(this);
        this.handleSubmitOut = this.handleSubmitOut.bind(this);
        this.handleChangeSDCard = this.handleChangeSDCard.bind(this);
        this.handleSubmitSDCard = this.handleSubmitSDCard.bind(this);
    }

    handleChangeOut(e){
        this.setState({outPath: e.target.value});
    }

    handleSubmitOut(e){
        post(`${process.env.REACT_APP_GLOBALS}/log_output_path`, this.state.outPath);
        e.preventDefault();
    }

    handleChangeSDCard(e){
        this.setState({SDCardPath: e.target.value});
    }

    handleSubmitSDCard(e){
        post(`${process.env.REACT_APP_GLOBALS}/sd_card_path`, this.state.SDCardPath);
        post(`${process.env.REACT_APP_GLOBALS}/parse_sd_card`, true);
        e.preventDefault();
    }

    render(){
        return(
            <div>
                <form onSubmit={this.handleSubmitOut}>
                    <label>
                        Output Path:
                        <input type="text" value={this.state.outPath} onChange={this.handleChangeOut} />
                    </label>
                    <input type="submit" value="Submit" />
                </form>

                <form onSubmit={this.handleSubmitSDCard}>
                    <label>
                        Path to Data:
                        <input type="text" value={this.state.SDCardPath} onChange={this.handleChangeSDCard} />
                    </label>
                    <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default SDCardParser;