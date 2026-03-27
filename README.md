# Nvidia_paper_analysis
A small application to analyze a scientific paper using FastAPI and Nvidia LLM.

Several prompt engineering techniques were employed, including segmenting the paper into text chunks of 1, 2 or 3 pages.  
This approach made it possible to:
- avoid exceeding the LLM's context window;
- enhance the model's focus by preventing the dilution of attention across the entire document;
- reduce computational and token-related costs associated with large-context processing.


The app has been deployed on [koyeb](https://app.koyeb.com/) and can be accessed with the following link:
https://hurt-firefly-42e33as-a3f9167d.koyeb.app/
