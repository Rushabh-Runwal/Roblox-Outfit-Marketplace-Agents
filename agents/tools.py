"""Roblox catalog tools - one tool per part family with fixed subcategory and 10-item limit."""
from typing import Optional, Dict, Any, List
from camel.toolkits import FunctionTool
from agents.roblox_catalog_client import catalog_search, map_items


async def _search_with(subcategory: int, *, Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Internal helper for search with fixed subcategory and Limit=10."""
    params: Dict[str, Any] = {"Limit": 10, "Subcategory": subcategory}
    if Keyword: params["Keyword"] = Keyword
    if Genres is not None: params["Genres"] = Genres
    if MinPrice is not None: params["MinPrice"] = MinPrice
    if MaxPrice is not None: params["MaxPrice"] = MaxPrice
    raw = await catalog_search(params)
    return map_items(raw)  # default_slot handled inside if needed


# Concrete tool functions (names matter for the model)
async def search_hats(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for hats and helmets."""
    return await _search_with(9, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_faces(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for faces."""
    return await _search_with(10, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_hair(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for hair accessories."""
    return await _search_with(20, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_back_accessories(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for back accessories like wings, capes, jetpacks."""
    return await _search_with(25, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_neck_accessories(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for neck accessories like necklaces, scarfs."""
    return await _search_with(22, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_shoulder_accessories(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for shoulder accessories like pauldrons."""
    return await _search_with(23, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_front_accessories(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for front accessories like armor, chest gear."""
    return await _search_with(24, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_waist_accessories(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for waist accessories like belts, tails."""
    return await _search_with(26, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_shirts(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for shirts."""
    return await _search_with(12, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_tshirts(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for t-shirts."""
    return await _search_with(13, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_pants(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for pants."""
    return await _search_with(14, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_heads(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for head body parts."""
    return await _search_with(15, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_dynamic_heads(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for dynamic heads."""
    return await _search_with(66, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_bundles(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for bundles."""
    return await _search_with(37, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


async def search_emotes(Keyword: Optional[str]=None, Genres: Optional[int]=None, MinPrice: Optional[int]=None, MaxPrice: Optional[int]=None) -> List[dict]:
    """Search for emote animations."""
    return await _search_with(39, Keyword=Keyword, Genres=Genres, MinPrice=MinPrice, MaxPrice=MaxPrice)


# Export tool list for CAMEL
TOOLS = [
    FunctionTool(search_hats),
    FunctionTool(search_faces),
    FunctionTool(search_hair),
    FunctionTool(search_back_accessories),
    FunctionTool(search_neck_accessories),
    FunctionTool(search_shoulder_accessories),
    FunctionTool(search_front_accessories),
    FunctionTool(search_waist_accessories),
    FunctionTool(search_shirts),
    FunctionTool(search_tshirts),
    FunctionTool(search_pants),
    FunctionTool(search_heads),
    FunctionTool(search_dynamic_heads),
    FunctionTool(search_bundles),
    FunctionTool(search_emotes),
]