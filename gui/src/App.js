import './App.css';
import Tabs from './components/Tabs';
import React, { useState } from 'react';
import {post, get} from './helpers';
import ModelImport from './Model_import';
import SDCardParser from './SD_card_parser';

const tab_list = [
      {
          id: 1,
          tabTitle: 'Telemetry',
          task: 'xbee_task',
          content: 'This is where telem will go'
      },
      {
          id: 2,
          tabTitle: 'Model',
          task: 'model_import',
          content: <ModelImport/>
      },
      {
          id: 3,
          tabTitle: 'SD card Parsing',
          task: 'SD_card_parser',
          content: <SDCardParser/>
      }

  ];



function App(){

  const [activeTask, setActiveTask] = useState('xbee_task');
  const [currentTab, setCurrentTab] = useState('1');

  const handleTabClick = (e) => {
    setCurrentTab(e.target.id);

    const task_name = e.target.getAttribute('data-arg');
    setActiveTask(task_name);
    console.log("change task " + task_name);

    post(`${process.env.REACT_APP_GLOBALS}/active_task`, task_name)
  }

  return (
    <div className='App'>
      {Tabs({
              tabs: tab_list, 
              currentTab: currentTab,
              activeTask: activeTask,
              onClick: handleTabClick
            })}
    </div>
  );
}

export default App;
