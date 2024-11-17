/**
 * @file stateTable.js
 *
 * Represents a state table component used for displaying and managing table data.
 */

import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Box, MenuItem, Select, SelectChangeEvent } from '@mui/material';
import { API_HOST } from '../constants';
import RequestButton from './RequestButton';
import JsonView from '@uiw/react-json-view';

/**
 * Represents the structure of the table data.
 */
type TableData = {
  columns: GridColDef[];
  rows: any[][];
};

/**
 * Represents the StateTable component.
 */
const StateTable = (props: any) => {
  const [tableData, setTableData] = useState<TableData>({ columns: [], rows: [] });
  const [loading, setLoading] = useState(true);
  const [selectedOption, setSelectedOption] = useState('1');
  const [path, setPath] = useState('');
  const [routeData, setRouteData] = useState({ "data": "No Route Data yet" });
  const [timestamp, setTimestamp] = useState<string | null>(null);
  const [menuItems, setMenuItems] = useState<any>({});

  /**
   * Handles the change in the selected option.
   *
   * @param {SelectChangeEvent} event - The select change event.
   */
  const handleChange = (event: SelectChangeEvent) => {
    setSelectedOption(event.target.value as string);
  };

  /**
   * Fetches transition data on every render.
   */
  useEffect(() => {
    fetchData();
  }, [selectedOption]);

  /**
   * Fetches transition data from the API.
   */
  const fetchData = async () => {
    try {
      const response = await fetch(`${API_HOST}/get-all-transition-tables`);

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();

      const items: any = {};
      Object.keys(data.transition_tables).forEach((index) => {
        items[data.transition_tables[index]["path"]] = parseInt(index);
      });
      setMenuItems(items);

      if (data && data.transition_tables[selectedOption]["path"]) {
        setPath(data.transition_tables[selectedOption]["path"]);
        const transformedData = transformData(data);
        setTableData(transformedData);
        setTimestamp(data.timestamp);
      } else {
        console.error('Invalid data format:', data);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  /**
   * Transforms the fetched data into the rformat that can be displayed in MUI table component.
   *
   * @param {any} data - The data fetched from the API.
   * @returns {TableData} - The transformed table data.
   */
  const transformData = (data: any): TableData => {
    const columns = Object.keys(data.transition_tables[selectedOption]["df"]).map((key) => ({
      field: key,
      headerName: key,
      width: 300,
    }));

    const rows = Object.values(data.transition_tables[selectedOption]["df"]["SOURCE"]).map((key, index) => {
      const row: any = { id: index + 1 };

      columns.forEach((column) => {
        const value = data.transition_tables[selectedOption].df[column.field][index] ?? "";

        row[column.field] = value !== undefined ? value : "";
      });

      return row;
    });

    return { columns, rows };
  };

  return (
    <div style={{ display: "flex", flexDirection: "row" }}>
      <Box>
        <div style={{ margin: '10px', display: 'flex', justifyContent: 'flex-start' }}>
          <Select value={selectedOption} onChange={handleChange}>
            {Object.keys(menuItems).map((key) => (
              <MenuItem key={key} value={menuItems[key]}>
                {key}
              </MenuItem>
            ))}
          </Select>
        </div>
        <div style={{ margin: "10px", width: "2000px" }}>
          <DataGrid columns={tableData.columns} rows={tableData.rows} loading={loading} autoHeight />
        </div>
      </Box>
      <div style={{ margin: "10px" }}>
        {/* <RequestButton url={`${API_HOST}/get-sm-routes/${path}`} requestType={'GET'} responseHandler={setRouteData}></RequestButton> */}
        <div style={{ padding: "10px" }}>
          <JsonView value={routeData} collapsed={false} />
        </div>
      </div>
    </div>
  );
};

export default StateTable;
