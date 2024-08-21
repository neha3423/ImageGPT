import React, { useContext, useState, useEffect } from "react";
import "./Main.css";
import { assets } from "../../assets/assets";
import { Context } from "../../context/Context";
import stringSimilarity from "string-similarity";
import axios from "axios";

const Main = () => {
  const {
    RenderResult,
    onSent,
    recentPrompt,
    showResult,
    loading,
    resultData,
    setInput,
    setResultData,
    input,
  } = useContext(Context);

  const [selectedImages, setSelectedImages] = useState([]);
  const [sentQuery, setSentQuery] = useState(null);
  const [resImg , setresImg] = useState(null);
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedImages((prevImages) => [...prevImages, ...files]);
  };

  const preprocessImage = async (image) => {
    const formData = new FormData();
    formData.append("image", image);

    console.log("image" , formData.get("image"));
    try {
      const response = await axios.post('http://127.0.0.1:5000/preprocess_backend', formData, {
        responseType: 'blob', // Specify responseType as 'blob' to receive data as a Blob
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
  
      const base64Encoded = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(response.data);
      });
      ///const objectURL = URL.createObjectURL(response.data);

      return {
        inlineData: { data: base64Encoded, mimeType: response.data.type },
      };
    } catch (error) {
      console.error("Error preprocessing image:", error);
      return null;
    }
  };
  
  const handleSubmit = async () => {
    selectedImages.map((ele)=>{
      console.log(ele);
    })

    const preprocessedImages = await Promise.all(
      selectedImages.map(async (image) => {
        const processedPath = await preprocessImage(image);
        return processedPath ? processedPath : null;
      })
    );
  
    const validPreprocessedImages = preprocessedImages.filter(image => image !== null);
    console.log("preprocessed img " ,validPreprocessedImages);
    setresImg(null);
    if (input.trim().toLowerCase().includes("caption")) {
      console.log("image captioning inside fun");
      const captions = await performImageCaptioning(validPreprocessedImages);
      console.log(captions);
     await RenderResult({caption : captions , input : input.trim().toLowerCase()}); // write this in all required methods ,this parses the resukt in front end 
      setSelectedImages([]);
      setInput("");
      return captions; // Return the captions directly
    } 
    else if (input.trim().toLowerCase().includes("edge")) {
      const edgeDetectedImages = await performEdgeDetection(validPreprocessedImages);
      setSelectedImages([]);
      setInput("");
      return edgeDetectedImages; // Return the edge-detected images directly
    } 
    else if (input.trim().toLowerCase().includes("object") || input.trim().toLowerCase().includes("windmill") ) {
      const objectDetectedImages = await performObjectDetection(validPreprocessedImages);
      setSelectedImages([]);
      setInput("");
      return objectDetectedImages; // Return the edge-detected images directly
    } 
else if (input.trim().toLowerCase().includes("scene") || input.trim().toLowerCase().includes("classify") ) {
  console.log("Scene classification inside fun");
  const captions = await performSceneClassification(validPreprocessedImages);
  console.log(captions);
 await RenderResult({caption : captions , input : input.trim().toLowerCase()}); // write this in all required methods ,this parses the resukt in front end 
  setSelectedImages([]);
  setInput("");
  return captions; // Return the captions directly
} 
    
    else {
      await onSent({ input: input.trim().toLowerCase(), images: validPreprocessedImages });
      setSentQuery({ input: input.trim().toLowerCase(), images: validPreprocessedImages });
      setSelectedImages([]);
      setInput("");
    }
  };
  
  const performImageCaptioning = async (images) => {
  
    // console.log(images[0])
    try {
      const response = await axios.post('http://127.0.0.1:5000/image_captioning',  {image : images}, {
        headers: {
            'Content-Type': 'application/json'
        }});
      console.log(response.data)
      
      return response.data.caption;
    } catch (error) {
      console.error("Error in image captioning:", error);
      return [];
    }
  };

  const performSceneClassification = async (images) => {
  
    // console.log(images[0])
    try {
      const response = await axios.post('http://127.0.0.1:5000/scene_classification',  {image : images}, {
        headers: {
            'Content-Type': 'application/json'
        }});
      console.log(response.data)
      
      return response.data.output_text;
    } catch (error) {
      console.error("Error in image captioning:", error);
      return [];
    }
  };
  // const b64toBlob = (b64Data, contentType='', sliceSize=512) => {
  //   const byteCharacters = atob(b64Data);
  //   const byteArrays = [];
  
  //   for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
  //     const slice = byteCharacters.slice(offset, offset + sliceSize);
  
  //     const byteNumbers = new Array(slice.length);
  //     for (let i = 0; i < slice.length; i++) {
  //       byteNumbers[i] = slice.charCodeAt(i);
  //     }
  
  //     const byteArray = new Uint8Array(byteNumbers);
  //     byteArrays.push(byteArray);
  //   }
      
  //   const blob = new Blob(byteArrays, {type: contentType});
  //   return blob;
  // }
  
  const performEdgeDetection = async (images) => {
    
    try {
      const response = await axios.post('http://127.0.0.1:5000/edge_detection', {image : images}, {
        headers: {
            'Content-Type': 'application/json'
        },
       responseType: 'blob'
      });
      const objectURL = URL.createObjectURL(response.data);
      // setresImg((prev) => {
      //   // Ensure prev is initialized as an array if it's undefined or null
      //   const prevArray = Array.isArray(prev) ? prev : [];
      
      //   return [...prevArray, objectURL];
      // });
      setresImg([objectURL]);
          // Ensure prev is initialized as an array if it's undefined or null
          //const prevArray = Array.isArray(prev) ? prev : [];
        

        
    RenderResult("your image is ");
        
    } catch (error) {
      console.error("Error in edge detection:", error);
      return [];
    }
  };

  const performObjectDetection = async (images) => {
    
    try {
      const response = await axios.post('http://127.0.0.1:5000/object_detection', {image : images}, {
        headers: {
            'Content-Type': 'application/json'
        },

       responseType: 'blob'
      
      });   
      const objectURL = URL.createObjectURL(response.data);
      setresImg([objectURL]);
        
    RenderResult("your image is ");
        
    } catch (error) {
      console.error("Error in object detection:", error);
      return [];
    }
  };

  useEffect(() => {
    if (showResult) {
      setSelectedImages([]);
    }
  }, [showResult]);
  
  return (
    <div className="main">
      <div className="nav">
        <p>ImageGPT</p>
        <img src={assets.user_icon} alt="" />
      </div>
      <div className="main-container">
        {!showResult ? (
          <div className="greet">
            <p>
              <span>Hello, Developer.</span>
            </p>
            <p>How can I help you today?</p>
          </div>
        ) : (
          <div className="result">

            <div className="result-title">
              <img src={assets.user_icon} alt="" />
              <p className="prompt">{recentPrompt}</p> {/* Input prompt */}
            </div>
            <div className="result-title-images">
              {sentQuery && sentQuery.images.length > 0 && (
                <div className="selected-images">
                  {sentQuery.images.map((image, index) => (
                    <div key={index} style={{ display: "block", marginRight: "5px", marginBottom: "5px" }}>
                      {/* <img
                        src={URL.createObjectURL(image)}
                        alt={Selected ${index}}
                        style={{ width: "100px", height: "100px" }}
                      /> */}
                    </div>
                  ))}
                </div>
              )}
              
            </div>
            <div className="res-imgs">

            {resImg &&  (
                <div className="selected-images1">
                  {resImg.map((image, index) => (
                    <div key={index} style={{ display: "block", marginRight: "5px", marginBottom: "5px" }}>
                      <img
                        src={image}
                        alt={`Selected ${index}`}
                        style={{ width: "400px", height: "400px" }}
                      />
                    </div>
                  ))}
                </div>
              )}

              </div>
            <div className="result-data">
              <img src={assets.gemini_icon} alt="" />
              {loading ? (
                <div className="loader">
                  <hr />
                  <hr />
                  <hr />
                </div>
              ) : (
                <>
                  <p
                    dangerouslySetInnerHTML={{
                      __html: resultData,
                    }}
                  ></p>
                </>
              )}
            </div>
          </div>
        )}

        <div className="main-bottom">
          <div className="search-box">
            <input
              onChange={(e) => setInput(e.target.value)}
              value={input}
              type="text"
              placeholder="Enter a prompt here"
              onKeyDown={handleKeyDown}
            />
            <div>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageChange}
                style={{ display: "none" }}
                id="image-upload"
              />
              <label htmlFor="image-upload">
                <img src={assets.gallery_icon} alt="Upload" style={{ cursor: "pointer" }} />
              </label>

              {input || selectedImages.length > 0 ? (
                <img
                  onClick={handleSubmit}
                  src={assets.send_icon}
                  alt=""
                />
              ) : null}
            </div>
          </div>
          {/* Display selected images */}
          {selectedImages.length > 0 && (
            <div className="selected-images">
              <p>Selected Images:</p>
              {selectedImages.map((image, index) => (
                <img
                  key={index}
                  src={URL.createObjectURL(image)}
                  alt={`Selected ${index}`}
                  style={{ width: "50px", height: "50px", marginRight: "5px" }}
                />
              ))}
            </div>
          )}
          <p className="bottom-info">
            Gemini may display inaccurate info, including about people, so
            double-check its responses. Your Privacy and Gemini Apps
          </p>
        </div>
      </div>
    </div>
  );
};

export default Main;