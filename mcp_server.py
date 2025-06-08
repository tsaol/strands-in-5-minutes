import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from strandsagents import StrandsAgents
from exa_py import Exa
import uvicorn

# Load environment variables
load_dotenv()

# Initialize API clients
exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
strands_client = StrandsAgents()

# Create FastAPI app
app = FastAPI(title="MCP Web Search Server")

class SearchRequest(BaseModel):
    query: str
    language: str = "中文"
    num_results: int = 5

@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Use Exa for web search
        search_results = exa_client.search(
            query=request.query,
            num_results=request.num_results,
            use_autoprompt=True
        )
        
        # Extract content and URLs from search results
        contents = []
        for result in search_results.results:
            contents.append({
                "title": result.title,
                "content": result.text,
                "url": result.url
            })
        
        # Use Strands to process and summarize the search results
        system_prompt = "你是一个专业的搜索助手。请根据搜索结果提供简洁明了的总结。" if request.language == "中文" else \
                       "You are a professional search assistant. Please provide a concise summary based on the search results."
        
        agent = strands_client.agent(system=system_prompt)
        
        # Create a prompt with the search results
        prompt = f"以下是关于'{request.query}'的搜索结果，请提供一个全面的总结:" if request.language == "中文" else \
                 f"Here are the search results for '{request.query}', please provide a comprehensive summary:"
        
        for i, content in enumerate(contents):
            prompt += f"\n\n结果 {i+1}:\n标题: {content['title']}\n内容: {content['content']}\n链接: {content['url']}"
        
        # Get response from Strands agent
        response = agent.complete(prompt)
        
        return {
            "query": request.query,
            "language": request.language,
            "summary": response,
            "results": contents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "MCP Web Search Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
