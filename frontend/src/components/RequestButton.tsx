import { Button } from '@mui/material';
import React from 'react';

interface RequestButtonProps {
  buttonText: string,
  url: string,
  requestType: string,
  requestData: object,
  responseHandler: (data: any) => void
}

const RequestButton: React.FC<RequestButtonProps> = ({buttonText, url, requestType, requestData, responseHandler }) => {
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
      responseHandler(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <Button variant="outlined" color="primary" onClick={handleClick}>
      {buttonText}
    </Button>
  );
};

export default RequestButton;
