# Import all models to ensure they are known to the Base metadata
from .user import User
from .review import Review
from .product import Product, ProductSize
from .order import Order, OrderItem
from .category import Category
from .cart import Cart, CartItem, Cart_Item
from .support import PolicyDocument, SupportTicket
from .knowledge import KnowledgeDocument, DocumentChunk

models_arr = [User, Review, Order, OrderItem,
              Product, ProductSize, Category, Cart, CartItem,
              PolicyDocument, SupportTicket, KnowledgeDocument, DocumentChunk]
