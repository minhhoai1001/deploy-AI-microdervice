from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Farm(Base):
    __tablename__ = "farm"
    
    farm_id = Column(Integer, primary_key=True)
    farm_name = Column(String(30), nullable=False)
    farm_location = Column(String(50), nullable=False)

    cages = relationship("Cage", back_populates="farm")
    timeline = relationship("CageTimeLine", back_populates="farm")
    fish = relationship("Fish", back_populates="farm")

class Cage(Base):
    __tablename__ = "cage"

    cage_id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farm.farm_id"), nullable=False)
    cage_location = Column(String(50), nullable=False)
    cage_name = Column(String(30), nullable=False)

    farm = relationship("Farm", back_populates="cages")
    timeline = relationship("CageTimeLine", back_populates="cage")
    fish = relationship("Fish", back_populates="cage")

class CageTimeLine(Base):
    __tablename__ = "cagetimeline"

    timeline_id      = Column(Integer, primary_key=True)
    cage_id          = Column(Integer, ForeignKey("cage.cage_id"), nullable=False)
    farm_id          = Column(Integer, ForeignKey("farm.farm_id"), nullable=False)
    stocking_date    = Column(DateTime, nullable=False)
    harves_date      = Column(DateTime)

    farm = relationship("Farm", back_populates="timeline")
    cage = relationship("Cage", back_populates="timeline")
    fish = relationship("Fish", back_populates="timeline")

class Fish(Base):
    __tablename__ = "fish"

    fish_id          = Column(Integer, primary_key=True)
    cage_id          = Column(Integer, ForeignKey("cage.cage_id"), nullable=False)
    farm_id          = Column(Integer, ForeignKey("farm.farm_id"), nullable=False)
    timeline_id      = Column(Integer, ForeignKey("cagetimeline.timeline_id"), nullable=False)
    image_path       = Column(Text, nullable=False)
    capture_date     = Column(DateTime, nullable=False)
    weight           = Column(Numeric(5, 2))
    length           = Column(Numeric(5, 2))
    lice_adult_female = Column(Integer)
    lice_mobility    = Column(Integer)
    lice_attached    = Column(Integer)

    farm = relationship("Farm", back_populates="fish")
    cage = relationship("Cage", back_populates="fish")
    timeline = relationship("CageTimeLine", back_populates="fish")
