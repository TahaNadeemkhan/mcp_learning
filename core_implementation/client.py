from mcp import ClientSession, types
from mcp.client.streamable_http import streamablehttp_client
import asyncio
from contextlib import AsyncExitStack
import json
from pydantic import AnyUrl


class MCPClient:
    def __init__(self, url):
        self.url = url
        self.stack = AsyncExitStack()
        self._sess = None
  
    async def __aenter__(self):
        read, write, _ = await self.stack.enter_async_context(
            streamablehttp_client(self.url)
        )
        self._sess = await self.stack.enter_async_context(
            ClientSession(read, write)
        )   
        await self._sess.initialize()
        return self
    
    async def __aexit__(self, *args):
        await self.stack.aclose()
    
    async def list_tools(self):
        return (await self._sess.list_tools()).tools
    
    async def call_tool(self, tool_name, arguments: dict):
        return await self._sess.call_tool(tool_name, arguments) 
    
    async def ping(self):
        return await self._sess.send_ping()
    
    async def send_progress(self, progress_token, progress, total=None, message=None):
        return await self._sess.send_progress_notification(progress_token, progress, total, message)
    
    async def list_resources(self) -> types.Resource:
        assert self._sess, "Session not available"
        result: types.ListResourcesResult = await self._sess.list_resources()
        return result.resources
        
    async def list_resource_templates(self) -> types.ListResourceTemplatesResult:
        assert self._sess, "Session not available"
        result: types.ListResourceTemplatesResult = await self._sess.list_resource_templates()
        return result.resourceTemplates

    async def read_resources(self, uris: list[str]) -> types.ReadResourceResult:
        assert self._sess, "Session not available"
        result =  await self._sess.read_resource(AnyUrl(uris))
        resource =  result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                try:
                    return json.loads(resource.text)
                except json.JSONDecodeError:
                    raise ValueError(f"Failed to decode JSON from resource: {resource.text}")
        return resource.text
    
    
    
    # async def read_resource(self, uri: str):
    #     return await self._sess.read_resource(uri)


async def main():
    async with MCPClient(url="http://localhost:8000/mcp") as client:
        # tools = await client.list_tools()
        # # print("Tools:", tools)
       
        data = await client.read_resources("binary://logo")
        print("First 100 chars of base64:", data[:100])

    #    resources = await client.list_resource_templates()
    #    intro_template = print("Resource Templates:", resources[0].uriTemplate.replace("{doc_id}", "deposition.md"))
    #    print(intro_template)

    #    data = await client.read_resources("docs://documents")
    #    print("Data: ", str(data))
    #    for r in resources:
    #        data = await client.read_resources(r.uri)
    #        print(f"Resource {r.uri} contents:", data)

asyncio.run(main())
