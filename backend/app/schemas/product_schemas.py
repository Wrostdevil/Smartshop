from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CategoryOut(BaseModel):
    name: str
    id: Optional[int] = None


class ProductSizeOut(BaseModel):
    size: str
    stock_quantity: int = 0
    size_id: Optional[int] = None


class AISummary(BaseModel):
    pros: List[str] = []
    cons: List[str] = []


class ProductOut(BaseModel):
    """ShopSmart storefront shape — exactly what the React adapter consumes."""

    id: Any
    slug: str
    name: str
    brand: str = ""
    category: str = "General"
    price: float = 0
    originalPrice: Optional[float] = None
    rating: float = 4.5
    reviewCount: int = 0
    availability: str = "IN_STOCK"
    stockCount: int = 0
    image: str = ""
    description: str = ""
    specs: Dict[str, Any] = {}
    aiSummary: AISummary = Field(default_factory=AISummary)
    tags: List[str] = []

    # Legacy aliases so old clients keep working
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    image_url: Optional[str] = None
    blurb: Optional[str] = None
    sale_price: Optional[float] = None
    categories: List[Any] = []
    sizes: List[Any] = []


class ProductCreate(BaseModel):
    slug: str
    name: Optional[str] = None
    product_name: Optional[str] = None
    brand: str = ""
    category: str = "General"
    product_type: Optional[str] = None
    price: float = Field(gt=0)
    originalPrice: Optional[float] = None
    sale_price: Optional[float] = None
    rating: float = 4.5
    reviewCount: int = 0
    availability: str = "IN_STOCK"
    stockCount: int = 10
    image: Optional[str] = None
    image_url: Optional[str] = None
    description: str = ""
    blurb: Optional[str] = None
    specs: Dict[str, Any] = {}
    aiSummary: Optional[AISummary] = None
    tags: List[str] = []


# Legacy names kept for old imports
ProductBase = ProductOut
ProductResponse = ProductOut
CategoryBase = CategoryOut
CategoryResponse = CategoryOut
ProductSizeBase = ProductSizeOut
ProductSizeResponse = ProductSizeOut


class ProductListOut(BaseModel):
    products: List[ProductOut]
    total: int = 0
    page: int = 0
    limit: int = 50


class CatalogMeta(BaseModel):
    categories: List[str] = []
    brands: List[str] = []
    priceCeil: int = 2000
    total: int = 0
