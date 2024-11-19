import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import RequestButton from './RequestButton';

interface NodeProps {
  data: {
    buttonText: string;
    url: string;
    requestType: string;
    requestData: any;
  };
}

const Node: React.FC<NodeProps> = ({ data }) => {
  return (
    <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}>
      <CardContent>
        <RequestButton
          buttonText={data.buttonText}
          url={data.url}
          requestType={data.requestType}
          requestData={data.requestData}
        />
      </CardContent>
    </Card>
  );
};

export default Node;
