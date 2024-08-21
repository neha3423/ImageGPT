import {
  GoogleGenerativeAI,
  HarmCategory,
  HarmBlockThreshold,
} from "@google/generative-ai";

const MODEL_NAME = "gemini-1.5-flash";
const API_KEY = "<API_KEY_VALUE";

async function runChat(prompt) {
  const genAI = new GoogleGenerativeAI(API_KEY);
  const model = genAI.getGenerativeModel({ model: MODEL_NAME });

  const generationConfig = {
    temperature: 0.9,
    topK: 1,
    topP: 1,
    maxOutputTokens: 2048,
  };

  const safetySettings = [
    {
      category: HarmCategory.HARM_CATEGORY_HARASSMENT,
      threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
      category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
      threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
      category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
      threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
      category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
      threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
  ];

  try {
    const chat = await model.startChat({
      generationConfig,
      safetySettings,
      history: [],
    });

    // Ensure the prompt is a string
    // if (typeof prompt !== 'string') {
    //   throw new TypeError("The prompt should be a string.");
    // }


    //experiment with

    const result = await model.generateContent(prompt); //line to generate iamge and text
        // const result = await chat.sendMessage(prompt);

    const response= await result.response;
    const text = response.text();
    console.log(text);

    //
    // const result = await chat.sendMessage(prompt);
    // const response = result.response;

    // Verify response is an object and has the text method
    if (!response || typeof response.text !== 'function') {
      throw new TypeError("Invalid response format received from the API.");
    }

    // const responseText = await response.text();
    // console.log(responseText); // Logging the response text

    return text;
  } catch (error) {
    console.error("Error in runChat:", error);
    throw error;
  }
}

export default runChat;
