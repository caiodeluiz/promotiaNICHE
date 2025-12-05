import { GoogleGenAI, Type } from "@google/genai";
import { GeneratedListing, Platform } from "../types";

/**
 * Generates a product listing based on an image and selected platform.
 */
export const generateListing = async (
  base64Image: string,
  platform: Platform
): Promise<GeneratedListing> => {
  // Initialize the client inside the function to pick up the latest process.env.API_KEY
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  try {
    const prompt = `
      Analyze the provided product image and generate a high-converting listing for ${platform}.
      Return the result in JSON format with the following fields:
      - title: An SEO-optimized title suitable for ${platform}.
      - description: A persuasive product description (marketing copy).
      - pricePrediction: An estimated price range (e.g., "$25.00 - $35.00").
      - tags: A list of 5-10 relevant keywords.
      - features: A list of 3-5 key features/bullet points.
      - platformSpecific: A short tip specific to selling this item on ${platform}.
    `;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: "image/jpeg", // Assuming JPEG for simplicity, can be dynamic
              data: base64Image,
            },
          },
          { text: prompt },
        ],
      },
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING },
            description: { type: Type.STRING },
            pricePrediction: { type: Type.STRING },
            tags: { type: Type.ARRAY, items: { type: Type.STRING } },
            features: { type: Type.ARRAY, items: { type: Type.STRING } },
            platformSpecific: { type: Type.STRING },
          },
        },
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from AI");
    
    return JSON.parse(text) as GeneratedListing;
  } catch (error) {
    console.error("Error generating listing:", error);
    throw error;
  }
};
