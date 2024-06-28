//This code was adapted from https://github.com/rojaslabs/react-simple-tabs

import React from 'react';

const Tabs = (props) => {

    return (
        <div>
            <div className='tabs'>
                {props.tabs.map((tab, i) =>
                    <button 
                        key={i} 
                        id={tab.id} 
                        data-arg = {tab.task} 
                        disabled={props.currentTab === `${tab.id}`} 
                        onClick={props.onClick}
                    >{tab.tabTitle}</button>
                )}
            </div>
            <div className='content'>
                {props.tabs.map((tab, i) =>
                    <div key={i}>
                        {props.currentTab === `${tab.id}` && <div>{tab.content}</div>}
                    </div>
                )}
            </div>
        </div>
    );
}


export default Tabs;

