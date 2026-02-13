from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin / staff
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sales = relationship("Sale", back_populates="user", lazy="select")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(String, nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    
    # Relationships
    sale_items = relationship("SaleItem", back_populates="product", lazy="select")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', type='{self.type}', size='{self.size}')>"


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sales", lazy="joined")
    items = relationship("SaleItem", back_populates="sale", lazy="select", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale(id={self.id}, total={self.total}, payment_method='{self.payment_method}')>"


class SaleItem(Base):
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of sale
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items", lazy="joined")
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.price
    
    def __repr__(self):
        return f"<SaleItem(id={self.id}, sale_id={self.sale_id}, product_id={self.product_id}, quantity={self.quantity})>"
