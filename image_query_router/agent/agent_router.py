from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools.caption import caption_image_tool
from tools.search_similar import search_similar_image_tool
from tools.search_text import search_image_by_text_tool
from tools.index_images import index_images_to_the_stores as index_images_to_the_stores

# Initialize LLM
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# Register tools
tools = [
    caption_image_tool,
    search_similar_image_tool,
    search_image_by_text_tool,
    index_images_to_the_stores
]

# Initialize the agent using OpenAI Functions
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    return_direct=True
)
