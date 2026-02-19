"""Import all ORM models so SQLAlchemy's metadata is fully populated."""
from models.base import Base  # noqa: F401
from models.user import User  # noqa: F401
from models.economy import Department, GDPPerCapita, Inflation, Unemployment, Export, PublicContract  # noqa: F401
from models.politics import ElectionResult, DemocracyIndex, CorruptionIndex, SocialConflict, TIOCTerritory  # noqa: F401
from models.technology import InternetPenetration, CoverageZone, RDSpending, DigitalLiteracy  # noqa: F401
from models.society import HDIIndex, LifeExpectancy, NutritionIndicator, CensusData, GenderGapIndex, BasicServices  # noqa: F401
from models.environment import DeforestationZone, ProtectedArea, MiningConcession, LithiumSaltFlat, CO2Emission, ForestFire  # noqa: F401
from models.security import CrimeRate, DrugSeizure, RoadSegment, Prison, HealthcareFacility  # noqa: F401
