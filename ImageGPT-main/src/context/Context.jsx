import { createContext, useState } from "react"; // Importing createContext and useState hooks from React
import runChat from "../config/gemini"; // Importing the runChat function from the configuration file

// Creating a new context
export const Context = createContext();


// ContextProvider component
const ContextProvider = (props) => {
  // State variables
  const [input, setInput] = useState(""); // Input state
  const [recentPrompt, setRecentPrompt] = useState(""); // Recent prompt state
  const [prevPrompts, setPrevPrompts] = useState([]); // Previous prompts state
  const [showResult, setShowResult] = useState(false); // Show result state
  const [loading, setLoading] = useState(false); // Loading state
  const [resultData, setResultData] = useState(""); // Result data state

  // Function to handle new chat
  const newChat = () => {
    setLoading(false);
    setShowResult(false);
  };

  async function fileToGenerativePart(file) {
    const base64EncodedDataPromise =   new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.readAsDataURL(file);
    });
    return {
      inlineData: { data: await base64EncodedDataPromise, mimeType: file.type },
    };
  }

  
const RenderResult = async (props) =>{
  setResultData(""); // Clear previous result data
  setLoading(true); // Set loading to true
  setShowResult(true); // Show result
  setPrevPrompts((prev) => [...prev, props.input]); // Add input to previous prompts
      setRecentPrompt(input); // Set recent prompt
  setResultData(props.caption);
  setLoading(false); // Set loading to false
  setInput(""); // Clear input
}

  const onSent = async (prompt) => {
    setResultData(""); // Clear previous result data
    setLoading(true); // Set loading to true
    setShowResult(true); // Show result
    console.log(prompt.images);
    let arr = prompt.images;
    let response;
    let inputToProcess;

  //   const imageParts = await Promise.all(
  //   [...arr].map(fileToGenerativePart)
  // );

  arr.map((ele)=>{
    console.log(ele)
  })
    if (typeof prompt === 'object') {
      inputToProcess = [prompt.input,...arr];
    } else {
      inputToProcess = prompt;
    }
  console.log(prompt);
    // Use the correct input value
    if (inputToProcess !== undefined) {
      response = await runChat(inputToProcess); // Run chat with the provided prompt
      setRecentPrompt([prompt.input]); // Set recent prompt
    } else {
      setPrevPrompts((prev) => [...prev, input]); // Add input to previous prompts
      setRecentPrompt(input); // Set recent prompt
      response = await runChat(input); // Run chat with input
    }
  console.log(response);
    // Processing response for formatting
    let responseArray = response.split("");
    let newResponse = "";
    for (let i = 0; i < responseArray.length; i++) {
      if (i === 0 || i % 2 !== 1) {
        newResponse += responseArray[i];
      } else {
        newResponse += "<b>" + responseArray[i] + "</b>";
      }
    }
    let newResponse2 = newResponse.split("*").join("</br>");
    let newResponseArray = newResponse2.split(" ");
    console.log(typeof newResponseArray);7

   
    // Function to simulate typing effect
    const delayPara = (index, nextWord) => {
      setTimeout(function () {
        setResultData((prev) => prev + nextWord);
      }, 75 * index);
    };
  
    // Triggering typing effect for each word in the response
    for (let i = 0; i < newResponseArray.length; i++) {
      const nextWord = newResponseArray[i];
      delayPara(i, nextWord + " ");
    }
    // setResultData("sdfd")
    setLoading(false); // Set loading to false
    setInput(""); // Clear input
  };

  // Value of the context
  const contextValue = {
    RenderResult,
    prevPrompts,
    setPrevPrompts,
    onSent,
    setRecentPrompt,
    recentPrompt,
    showResult,
    loading,
    resultData,
    setResultData,

    input,
    setInput,
    newChat,
  };

  // Providing context value to children components
  return (
    <Context.Provider value={contextValue}>{props.children}</Context.Provider>
  );
};

export default ContextProvider; // Exporting the ContextProvider component as default