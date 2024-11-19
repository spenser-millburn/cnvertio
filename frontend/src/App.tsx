import React from 'react'; 
import './App.css'; 
import FlowUI from './components/Flow';

export default function App() { 

  return ( 
    <div className="App" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}> 
      <FlowUI></FlowUI>
    </div> 
  ); 
}
