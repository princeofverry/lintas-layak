import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [detections, setDetections] = useState(null);
  const [imageSrc, setImageSrc] = useState(null);
  const [numPotholes, setNumPotholes] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  const onFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const onFileUpload = async () => {
    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:5000/detect', formData);

      const { detections, num_potholes, image } = response.data;
      setDetections(detections);
      setNumPotholes(num_potholes);

      // Convert the hex string back to a blob
      const byteArray = new Uint8Array(image.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
      const blob = new Blob([byteArray], { type: 'image/png' });
      const imageObjectURL = URL.createObjectURL(blob);
      setImageSrc(imageObjectURL);
    } catch (error) {
      console.error("Error uploading the file", error.response ? error.response.data : error.message);
    }
  };

  return (
    <div className="App">
      <h1>Object Detection</h1>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload</button>
      {imageSrc && (
        <div>
          <h2>Detection Image:</h2>
          <img src={imageSrc} alt="Detection result" />
        </div>
      )}
      {detections && (
        <div>
          <h2>Detections:</h2>
          <p>Number of potholes detected: {numPotholes}</p>
          <button onClick={() => setShowDetails(!showDetails)}>
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
          {showDetails && (
            <pre>{JSON.stringify(detections, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
