"""Data item definitions using plain dataclasses (no Scrapy dependency)."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ElectionResultItem:
    year: Optional[int] = None
    election_type: Optional[str] = None
    department: Optional[str] = None
    party: Optional[str] = None
    candidate: Optional[str] = None
    votes: Optional[int] = None
    percentage: Optional[float] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None


@dataclass
class ConflictItem:
    title: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None


@dataclass
class EconomicDataItem:
    indicator: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    department: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None


@dataclass
class ContractItem:
    sicoes_id: Optional[str] = None
    title: Optional[str] = None
    amount: Optional[float] = None
    contractor: Optional[str] = None
    department: Optional[str] = None
    date: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None


@dataclass
class EnvironmentItem:
    indicator: Optional[str] = None
    year: Optional[int] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    geometry_wkt: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: Optional[str] = None
