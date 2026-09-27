from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# 1. Профиль ИП 
class BusinessProfile(Base):
    __tablename__ = 'business_profiles'
    
    id = Column(Integer, primary_key=True)
    max_user_id = Column(String, unique=True, nullable=False) # ID из MAX
    industry = Column(String)        # Отрасль ("кофейня", "IT")
    region = Column(String)          # Регион ("Республика Татарстан")
    initial_capital = Column(Float)  # Начальный капитал
    monthly_revenue = Column(Float)  # Текущая выручка
    expenses = Column(JSON)          # {"rent": 50000, "salary": 30000}
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь с заявками
    applications = relationship("UserApplication", back_populates="profile")

# 2. База мер поддержки (Источник: МСП.РФ)
class SupportProgram(Base):
    __tablename__ = 'support_programs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)      # Название программы
    type = Column(String)                      # "субсидия", "кредит", "грант"
    amount_min = Column(Float)                 # Мин. сумма
    amount_max = Column(Float)                 # Макс. сумма
    interest_rate = Column(String, nullable=True) # Ставка для кредитов
    conditions = Column(JSON)                  # {"region": ["Татарстан"], "industry": ["IT"], "max_revenue": 2000000}
    source_url = Column(String)                # Ссылка на первоисточник (МСП.РФ)
    updated_at = Column(DateTime, default=datetime.utcnow) # Дата актуальности

# 3. Выбранные пользователем программы (Связующее звено)
class UserApplication(Base):
    __tablename__ = 'user_applications'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('business_profiles.id'))
    program_id = Column(Integer, ForeignKey('support_programs.id'))
    status = Column(String, default="selected") # selected, applied, received
    amount_selected = Column(Float)             # Сумма, которую выбрал пользователь
    
    profile = relationship("BusinessProfile", back_populates="applications")
    program = relationship("SupportProgram")

# 4. База блогеров (Для модуля маркетинга)
class Blogger(Base):
    __tablename__ = 'bloggers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)              # Имя/Ник
    niche = Column(String)             # Ниша ("еда", "бизнес", "мода")
    region = Column(String)            # Регион (или "РФ" для федеральных)
    followers = Column(Integer)        # Подписчики
    engagement_rate = Column(Float)    # Вовлеченность (например, 0.05)
    post_price = Column(Float)         # Стоимость поста
    platform = Column(String)          # "Instagram", "Telegram", "VK"