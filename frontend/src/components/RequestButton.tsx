import React, { useState } from 'react';
import { Button } from '@mui/material';
import JsonView from '@uiw/react-json-view';

interface RequestButtonProps {
  buttonText: string,
  url: string,
  requestType: string,
  requestData: object
}

const RequestButton: React.FC<RequestButtonProps> = ({ buttonText, url, requestType, requestData }) => {
  const [response, setResponse] = useState({ "data": "No Data yet" });

  const handleClick = () => {
    fetch(url, {
      method: requestType,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        setResponse(data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  return (
    <div>
      <Button variant="outlined" color="primary" onClick={handleClick}>
        {buttonText}
      </Button>
      <JsonView value={response} collapsed={false} />
    </div>
  );
};

export default RequestButton;